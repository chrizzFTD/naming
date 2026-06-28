"""Temporary fix for sphinx-pyrepl-web autodoc doctest REPLs.

Remove once https://github.com/chrizzFTD/sphinx-pyrepl-web includes:
- blank lines between separate doctest examples in replay scripts
- packages= loading for installed modules instead of exec'ing module source
"""

from __future__ import annotations

import importlib
import inspect
import sys
from pathlib import Path

from sphinx import addnodes


def apply() -> None:
    import sphinx_pyrepl_web as spw

    def extract_doctest_source(text: str) -> str:
        examples = spw._DOCTEST_PARSER.get_examples(text)
        if not examples:
            return ""

        lines: list[str] = []
        for index, example in enumerate(examples):
            if index:
                lines.append("")
            lines.extend(example.source.splitlines())
        return "\n".join(lines) + "\n"

    def make_pyrepl_raw(
        replay_src: str,
        src: str | None = None,
        packages: str | None = None,
    ):
        attrs = ["no-header", "no-banner", f'replay-src="{replay_src}"']
        if packages:
            attrs.insert(0, f'packages="{packages}"')
        if src:
            attrs.insert(0, f'src="{src}"')
        attr_str = " ".join(attrs)
        from docutils import nodes

        return nodes.raw("", f"<py-repl {attr_str}></py-repl>\n", format="html")

    def _resolve_autodoc_bootstrap(app, env, docname: str, desc: addnodes.desc):
        if not app.config.pyrepl_autodoc_bootstrap:
            return None, None, None

        sig = desc.next_node(addnodes.desc_signature)
        if sig is None:
            return None, None, None

        module_name = sig.get("module")
        fullname = sig.get("fullname")
        if not module_name:
            return None, None, None

        try:
            mod = sys.modules.get(module_name)
            if mod is None:
                mod = importlib.import_module(module_name)
            obj = mod
            if fullname:
                for part in fullname.split("."):
                    obj = getattr(obj, part)
            mod_obj = inspect.getmodule(obj) or mod
            source_path = Path(inspect.getfile(mod_obj)).resolve()
            srcdir = Path(env.srcdir).resolve()
            try:
                source_path.relative_to(srcdir)
                return spw.register_startup_file(env, docname, source_path), None, None
            except ValueError:
                return None, None, module_name.split(".")[0]
        except (AttributeError, ImportError, OSError, TypeError):
            return None, None, None

    def transform_doctest_blocks(app, doctree):
        scope = app.config.pyrepl_doctest_blocks
        if not scope:
            return

        from docutils import nodes

        env = app.env
        docname = env.docname
        replaced = False
        for node in doctree.findall(nodes.doctest_block):
            if scope == "autodoc" and not spw._inside_autodoc_desc(node):
                continue
            source = extract_doctest_source(node.astext())
            if not source.strip():
                continue
            bootstrap_src = None
            bootstrap_content = None
            packages = None
            desc = spw._find_autodoc_desc(node)
            if desc is not None:
                bootstrap_src, bootstrap_content, packages = _resolve_autodoc_bootstrap(
                    app, env, docname, desc
                )
            replay_src, startup_src = spw.register_autodoc_repl(
                env,
                docname,
                source,
                bootstrap_src=bootstrap_src,
                bootstrap_content=bootstrap_content,
            )
            node.replace_self(make_pyrepl_raw(replay_src, startup_src, packages))
            replaced = True

        if replaced:
            env.metadata[docname]["pyrepl"] = True
            doctree["pyrepl"] = True

    spw.extract_doctest_source = extract_doctest_source
    spw.make_pyrepl_raw = make_pyrepl_raw
    spw._resolve_autodoc_bootstrap = _resolve_autodoc_bootstrap
    spw.transform_doctest_blocks = transform_doctest_blocks
