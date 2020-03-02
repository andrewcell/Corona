import nltk
from PyInstaller.utils.hooks import collect_data_files

# add datas for nltk
datas = collect_data_files('nltk', False)

# loop through the data directories and add them
# for p in nltk.data.path:
#     datas.append((p, "nltk_data"))

datas.append(("<path_to_nltk_data>", "nltk_data"))

# nltk.chunk.named_entity should be included
hiddenimports = ["nltk.chunk.named_entity"]