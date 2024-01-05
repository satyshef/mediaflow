import lib.helper as Helper

#files = Helper.files_in_directory('./news')
#print(files)
files = Helper.files_in_directory('./news')

    # Вывести отсортированный список файлов
for file in files:
    print(file)