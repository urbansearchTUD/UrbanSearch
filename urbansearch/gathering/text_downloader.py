import os
from argparse import ArgumentParser
from multiprocessing import Process

from urbansearch.gathering import gathering, indices_selector
from urbansearch.utils import process_utils


class TextDownloader(object):

    def __init__(self):
        self.pd = gathering.PageDownloader()
        self.ind = indices_selector.IndicesSelector()

    def run_workers(self, num_workers, directory, output_dir,  **kwargs):
        """ Run workers to process indices from a directory with files
        in parallel. For each index the part will be downloaded and written
        in plain text to the output directory.

        :num_workers: Number of workers that will run
        :directory: Path to directory containing index files
        :output_dir: Output directory for plain text files
        :gz: Passed in kwargs. Files are in .gz format. Default: True
        :opt: Passed in kwargs. Determine optimal number of workers and
        ignore num_workers parameter
        """
        if kwargs.get('opt'):
            num_workers = process_utils.compute_num_workers()

        files = [_file.path for _file in os.scandir(directory)
                 if _file.is_file()]

        div_files = process_utils.divide_files(files, num_workers)
        workers = [Process(target=self.worker, args=(div_files[i], output_dir,
                                                     i, kwargs.get('gz', True)))
                   for i in range(num_workers)]

        for worker in workers:
            worker.start()

        # Wait for processes to finish
        for worker in workers:
            worker.join()

    def worker(self, files, output_dir, w_id, gz=True):
        """
        Worker that will parse indices from files in file list and put the
        write the results to separate files. Uses .gz files as input.

        :files: List of filepaths to files that this worker will use
        :output_dir: Output directory for the separate text files
        :w_id: Id of this worker, to prevent writing to same file
        :gz: Use .gz files or not, default: True.
        """
        rlv_indices = self.ind.relevant_indices_from_file
        if gz:
            for file in files:
                if file.endswith('.gz'):
                    for i, index in enumerate(rlv_indices(file)):
                        txt = self.pd.index_to_txt(index)
                        self._write_txt_file_index(index, txt, output_dir,
                                                   w_id, i)

    def _write_txt_file_index(self, index, text, output_dir, w_id, n):
        # Write index on first line of file, append the text
        final_text = str(index) + '\n' + text
        with open(os.path.join(output_dir, "W{0}-{1}.txt".format(w_id, n)),
                  "w") as f:
                f.write(final_text)

    def _parse_arguments(self):
        parser = ArgumentParser(description='UrbanSearch TextDownloader')
        parser.add_argument('directory',
                            help='Source files directory containing files with'
                                 + ' indices. .gz files only.')

        parser.add_argument('workers',
                            help='Number of parallel workers used')

        parser.add_argument('output',
                            help='Output directory where text containing at '
                                 + 'least 1 co-occurrence will be stored.')
        return parser.parse_args()


if __name__ == "__main__":
    td = TextDownloader()
    td.run_workers(2, '/home/gijs/BEP/UrbanSearch/tests/resources/indices_dir/', '/home/gijs/BEP/')
    #args = td._parse_arguments()

    #directory = args.directory
    #output_dir = args.output
    #workers = args.workers

    #td.run_workers(workers, directory, output_dir)