def _divide_files(files, parts):
    if files and parts > 0:
        files_len = len(files)
        if(parts > files_len):
            part_len = 1
        else:
            part_len = files_len // parts
        # Divide all files in 'equal' parts
        div_files = [files[i * part_len:part_len * (i + 1)]
                     for i in range(parts)]

        # If number of data entries is odd, append last file to last list
        if files_len % 2 != 0:
            div_files[-1] += [files[-1]]

        return div_files
    return None
