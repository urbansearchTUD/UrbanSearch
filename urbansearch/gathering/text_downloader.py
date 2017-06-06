from urbansearch.gathering import gathering, indices_selector
from urbansearch.utils import process_utils
from multiprocessing import Process
import os


class TextDownloader(object):

    def __init__(self):
        self.pd = gathering.PageDownloader()
        self.ind = indices_selector.IndicesSelector()

    def run_workers(self, num_workers, directory, output_dir,  **kwargs):
        """ Run workers to process indices from a directory with files
        in parallel. All parsed indices will be added to the queue.

        :num_workers: Number of workers that will run
        :directory: Path to directory containing files
        :queue: multiprocessing.Queue where the indices will be added to
        :gz: Passed in kwargs. Files are in .gz format. Default: True
        :opt: Passed in kwargs. Determine optimal number of workers and
        ignore num_workers parameter
        """
        if kwargs.get('opt'):
            num_workers = process_utils.compute_num_workers()

        files = [_file.path for _file in os.scandir(directory)
                 if _file.is_file()]

        div_files = process_utils.divide_files(files, num_workers)
        workers = [Process(target=self.worker, args=(div_files[i], output_dir, i,
                                                     kwargs.get('gz', True)))
                   for i in range(num_workers)]

        for worker in workers:
            worker.start()

        # Wait for processes to finish
        for worker in workers:
            worker.join()

    def worker(self, files, output_dir, w_id, gz=True):
        """
        Worker that will parse indices from files in file list and put the
        results in a Queue. Can use plain text files containing indices or
        .gz files containing indices.

        :queue: multiprocessing.JoinableQueue to put results in
        :files: List of filepaths to files that this worker will use
        :gz: Use .gz files or not, default: True.
        """
        if gz:
            i = 0
            for file in files:
                if file.endswith('.gz'):
                    for index in self.ind.relevant_indices_from_file(file):
                        txt = self.pd.index_to_txt(index)
                        self._write_txt_file_index(index, txt, output_dir, w_id, i)
                        i += 1

    def _write_txt_file_index(self, index, text, output_dir, w_id, n):
        final_text = str(index) + '\n' + text
        with open(output_dir + "W{0}-{1}.txt".format(w_id, n), "w") as text_file:
                text_file.write(final_text)

if __name__ == "__main__":
    td = TextDownloader()
    directory = '/home/gijs/BEP/test2/'
    output_dir = '/home/gijs/BEP/pages/'
    workers = 4 
    td.run_workers(workers, directory, output_dir)
