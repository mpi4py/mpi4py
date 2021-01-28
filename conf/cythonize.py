#!/usr/bin/env python
import sys, os

def cythonize(source,
              output=None,
              includes=(),
              destdir_c=None,
              destdir_h=None,
              wdir=None):
    import cyautodoc
    from Cython.Compiler.Main import \
         CompilationOptions, default_options, \
         compile, \
         PyrexError
    from Cython.Compiler import Options
    cwd = os.getcwd()
    try:
        if output is None:
            name, _ = os.path.splitext(source)
            output = name + '.c'
        else:
            name, _ = os.path.splitext(output)
        outputs_c = [output]
        outputs_h = [name + '.h', name + '_api.h']
        # change working directory
        if wdir:
            os.chdir(wdir)
        # run Cython on source
        options = CompilationOptions(default_options)
        if Options.directive_types['language_level'] is str:
            options.language_level = '3str'
        options.output_file = outputs_c[0]
        options.include_path = list(includes)
        Options.generate_cleanup_code = 3
        any_failures = 0
        try:
            result = compile(source, options)
            if result.num_errors > 0:
                any_failures = 1
        except (EnvironmentError, PyrexError):
            e = sys.exc_info()[1]
            sys.stderr.write(str(e) + '\n')
            any_failures = 1
        if any_failures:
            for output in outputs_c + outputs_h:
                try:
                    os.remove(output)
                except OSError:
                    pass
            return 1
        # move ouputs
        for destdir, outputs in (
            (destdir_c, outputs_c),
            (destdir_h, outputs_h)):
            if destdir is None: continue
            for output in outputs:
                dest = os.path.join(
                    destdir, os.path.basename(output))
                try:
                    os.remove(dest)
                except OSError:
                    pass
                os.rename(output, dest)
        #
        return 0
    #
    finally:
        os.chdir(cwd)

if __name__ == "__main__":
    sys.exit(
        cythonize('mpi4py/MPI.pyx', 'mpi4py.MPI.c',
                  destdir_h=os.path.join('mpi4py', 'include', 'mpi4py'),
                  wdir='src')
        )
