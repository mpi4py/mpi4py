#!/usr/bin/env python
import os
import sys


def cythonize(
    source,
    output=None,
    includes=(),
    workdir=None
):
    import cyautodoc
    from Cython.Compiler import Options
    from Cython.Compiler.Main import (
        CompilationOptions,
        default_options,
        compile,
        PyrexError,
    )
    cwd = os.getcwd()
    try:
        # compute output filenames
        if output is None:
            name, _ = os.path.splitext(source)
            output = name + '.c'
        else:
            name, _ = os.path.splitext(output)
        outputs_c = [output]
        outputs_h = [name + '.h', name + '_api.h']
        # run Cython on source
        options = CompilationOptions(default_options)
        lang_level = Options.directive_types.get('language_level', int)
        options.language_level = lang_level(3)
        options.output_file = output
        options.include_path = list(includes)
        options.working_path = workdir or ""
        Options.generate_cleanup_code = 3
        any_failures = 0
        try:
            if options.working_path:
                os.chdir(options.working_path)
            result = compile(source, options)
            if result.num_errors > 0:
                any_failures = 1
        except (EnvironmentError, PyrexError) as e:
            sys.stderr.write(str(e) + '\n')
            any_failures = 1
        if any_failures:
            for out in outputs_c + outputs_h:
                try:
                    os.remove(out)
                except OSError:
                    pass
            return 1
        return 0
    #
    finally:
        os.chdir(cwd)


if __name__ == "__main__":
    sys.exit(
        cythonize(
            'mpi4py/MPI.pyx',
            workdir='src',
        )
    )
