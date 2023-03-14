# ruff: noqa: UP008,UP031
from Cython.Compiler import Options
from Cython.Compiler import PyrexTypes
from Cython.Compiler.Visitor import CythonTransform
from Cython.Compiler.StringEncoding import EncodedString
from Cython.Compiler.AutoDocTransforms import (
    ExpressionWriter as BaseExpressionWriter,
    AnnotationWriter as BaseAnnotationWriter,
)


class ExpressionWriter(BaseExpressionWriter):

    def visit_UnicodeNode(self, node):
        self.emit_string(node, "")


class AnnotationWriter(ExpressionWriter, BaseAnnotationWriter):
    pass


class EmbedSignature(CythonTransform):

    def __init__(self, context):
        super(EmbedSignature, self).__init__(context)
        self.class_name = None
        self.class_node = None

    def _select_format(self, embed, clinic):
        return embed

    def _fmt_expr(self, node):
        writer = ExpressionWriter()
        result = writer.write(node)
        # print(type(node).__name__, '-->', result)
        return result

    def _fmt_annotation(self, node):
        writer = AnnotationWriter()
        result = writer.write(node)
        # print(type(node).__name__, '-->', result)
        return result

    def _fmt_arg(self, arg):
        annotation = None
        if arg.is_self_arg:
            doc = self._select_format(arg.name, '$self')
        elif arg.is_type_arg:
            doc = self._select_format(arg.name, '$type')
        else:
            doc = arg.name
            if arg.type is PyrexTypes.py_object_type:
                annotation = None
            else:
                annotation = arg.type.declaration_code('', for_display=1)
        if arg.annotation:
            annotation = self._fmt_annotation(arg.annotation)
        annotation = self._select_format(annotation, None)
        if annotation:
            doc = doc + (': %s' % annotation)
            if arg.default:
                default = self._fmt_expr(arg.default)
                doc = doc + (' = %s' % default)
        elif arg.default:
            default = self._fmt_expr(arg.default)
            doc = doc + ('=%s' % default)
        return doc

    def _fmt_star_arg(self, arg):
        arg_doc = arg.name
        if arg.annotation:
            annotation = self._fmt_annotation(arg.annotation)
            arg_doc = arg_doc + (': %s' % annotation)
        return arg_doc

    def _fmt_arglist(self, args,
                     npoargs=0, npargs=0, pargs=None,
                     nkargs=0, kargs=None,
                     hide_self=False):
        arglist = []
        for arg in args:
            if not hide_self or not arg.entry.is_self_arg:
                arg_doc = self._fmt_arg(arg)
                arglist.append(arg_doc)
        if pargs:
            arg_doc = self._fmt_star_arg(pargs)
            arglist.insert(npargs + npoargs, '*%s' % arg_doc)
        elif nkargs:
            arglist.insert(npargs + npoargs, '*')
        if npoargs:
            arglist.insert(npoargs, '/')
        if kargs:
            arg_doc = self._fmt_star_arg(kargs)
            arglist.append('**%s' % arg_doc)
        return arglist

    def _fmt_ret_type(self, ret):
        if ret is PyrexTypes.py_object_type:
            return None
        else:
            return ret.declaration_code("", for_display=1)

    def _fmt_signature(self, cls_name, func_name, args,
                       npoargs=0, npargs=0, pargs=None,
                       nkargs=0, kargs=None,
                       return_expr=None,
                       return_type=None, hide_self=False):
        arglist = self._fmt_arglist(args,
                                    npoargs, npargs, pargs,
                                    nkargs, kargs,
                                    hide_self=hide_self)
        arglist_doc = ', '.join(arglist)
        func_doc = '%s(%s)' % (func_name, arglist_doc)
        if cls_name:
            namespace = self._select_format('%s.' % cls_name, '')
            func_doc = '%s%s' % (namespace, func_doc)
        ret_doc = None
        if return_expr:
            ret_doc = self._fmt_annotation(return_expr)
        elif return_type:
            ret_doc = self._fmt_ret_type(return_type)
        if ret_doc:
            docfmt = self._select_format('%s -> %s', '%s -> (%s)')
            func_doc = docfmt % (func_doc, ret_doc)
        return func_doc

    def _embed_signature(self, signature, node_doc):
        if node_doc:
            docfmt = self._select_format("%s\n%s", "%s\n--\n\n%s")
            return docfmt % (signature, node_doc)
        else:
            return signature

    def __call__(self, node):
        if not Options.docstrings:
            return node
        else:
            return super(EmbedSignature, self).__call__(node)

    def visit_ClassDefNode(self, node):
        oldname = self.class_name
        oldclass = self.class_node
        self.class_node = node
        try:
            # PyClassDefNode
            self.class_name = node.name
        except AttributeError:
            # CClassDefNode
            self.class_name = node.class_name
        self.visitchildren(node)
        self.class_name = oldname
        self.class_node = oldclass
        return node

    def visit_LambdaNode(self, node):
        # lambda expressions so not have signature or inner functions
        return node

    def visit_DefNode(self, node):
        if not self.current_directives['embedsignature']:
            return node

        is_constructor = False
        hide_self = False
        if node.entry.is_special:
            is_constructor = self.class_node and node.name == '__init__'
            if not is_constructor:
                return node
            class_name, func_name = None, self.class_name
            hide_self = True
        else:
            class_name, func_name = self.class_name, node.name

        npoargs = getattr(node, 'num_posonly_args', 0)
        nkargs = getattr(node, 'num_kwonly_args', 0)
        npargs = len(node.args) - nkargs - npoargs
        signature = self._fmt_signature(
            class_name, func_name, node.args,
            npoargs, npargs, node.star_arg,
            nkargs, node.starstar_arg,
            return_expr=node.return_type_annotation,
            return_type=None, hide_self=hide_self)
        if signature:
            if is_constructor:
                doc_holder = self.class_node.entry.type.scope
            else:
                doc_holder = node.entry

            if doc_holder.doc is not None:
                old_doc = doc_holder.doc
            elif not is_constructor and getattr(node, 'py_func', None) is not None:
                old_doc = node.py_func.entry.doc
            else:
                old_doc = None
            new_doc = self._embed_signature(signature, old_doc)
            doc_holder.doc = EncodedString(new_doc)
            if not is_constructor and getattr(node, 'py_func', None) is not None:
                node.py_func.entry.doc = EncodedString(new_doc)
        return node

    def visit_CFuncDefNode(self, node):
        if not self.current_directives['embedsignature']:
            return node
        if not node.overridable:  # not cpdef FOO(...):
            return node

        signature = self._fmt_signature(
            self.class_name, node.declarator.base.name,
            node.declarator.args,
            return_type=node.return_type)
        if signature:
            if node.entry.doc is not None:
                old_doc = node.entry.doc
            elif getattr(node, 'py_func', None) is not None:
                old_doc = node.py_func.entry.doc
            else:
                old_doc = None
            new_doc = self._embed_signature(signature, old_doc)
            node.entry.doc = EncodedString(new_doc)
            py_func = getattr(node, 'py_func', None)
            if py_func is not None:
                py_func.entry.doc = EncodedString(new_doc)
        return node

    def visit_PropertyNode(self, node):
        if not self.current_directives['embedsignature']:
            return node

        entry = node.entry
        body = node.body
        prop_name = entry.name
        type_name = None
        if entry.visibility == 'public':
            # property synthesised from a cdef public attribute
            type_name = entry.type.declaration_code("", for_display=1)
            if not entry.type.is_pyobject:
                type_name = "'%s'" % type_name
            elif entry.type.is_extension_type:
                type_name = entry.type.module_name + '.' + type_name
        if type_name is None:
            for stat in body.stats:
                if stat.name != '__get__':
                    continue
                cls_name = self.class_name
                if cls_name:
                    namespace = self._select_format('%s.' % cls_name, '')
                    prop_name = '%s%s' % (namespace, prop_name)
                ret_annotation = stat.return_type_annotation
                if ret_annotation:
                    type_name = self._fmt_annotation(ret_annotation)
        if type_name is not None:
            signature = '%s: %s' % (prop_name, type_name)
            new_doc = self._embed_signature(signature, entry.doc)
            entry.doc = EncodedString(new_doc)
        return node


# Monkeypatch AutoDocTransforms.EmbedSignature
try:
    from Cython.Compiler import AutoDocTransforms
    AutoDocTransforms.EmbedSignature = EmbedSignature
except Exception as exc:
    import logging
    logging.Logger(__name__).exception(exc)

# Monkeypatch Nodes.raise_utility_code
try:
    from Cython.Compiler.Nodes import raise_utility_code
    code = raise_utility_code.impl
    ipos = code.index("if (tb) {\n#if CYTHON_COMPILING_IN_PYPY\n")
    raise_utility_code.impl = code[:ipos] + code[ipos:].replace(
        'CYTHON_COMPILING_IN_PYPY', '!CYTHON_FAST_THREAD_STATE', 1)
    del raise_utility_code, code, ipos
except Exception as exc:
    import logging
    logging.Logger(__name__).exception(exc)
