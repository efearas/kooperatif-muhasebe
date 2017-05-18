import pdb

def string_to_dictionary(string, elementSplitter , keyValueSplitter):	
	arr = string.split(elementSplitter)
	dic = {}
	for keyValue in arr:
		keyValuePairArr = keyValue.split(keyValueSplitter)
		dic[keyValuePairArr[0]] = keyValuePairArr[1]
	#pdb.set_trace()					
	return dic