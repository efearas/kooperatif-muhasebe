import pdb

def string_to_dictionary(string, elementSplitter , keyValueSplitter):	
	arr = string.split(elementSplitter)
	dic = {}
	for keyValue in arr:
		keyValuePairArr = keyValue.split(keyValueSplitter)
		dic[keyValuePairArr[0]] = keyValuePairArr[1]
	#pdb.set_trace()					
	return dic

def get_or_none(classmodel, **kwargs):
    try:
        return classmodel.objects.get(**kwargs)
    except classmodel.DoesNotExist:
        return None

def get_file_extension(_filename):
	arr = _filename.split(".")
	return arr[len(arr)-1]