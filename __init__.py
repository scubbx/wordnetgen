from __future__ import print_function
from nltk.corpus import wordnet as wn
import nltk
from Tkinter import *
import couchdb
from  pretty import *
import csv
import os
import itertools

def selectOnlyN(listOfSynsets):
    newListOfSynsets = []
    for word_synset in listOfSynsets:
        if word_synset.pos == 'n': newListOfSynsets.append(word_synset)
    return newListOfSynsets

def findSynsetsInWordnet(word_list):
    synset_list = []
    i = 1
    total = len(word_list)
    savedSynsets = readEntriesFromFile()
    for word in word_list:
        print(str(i) + " of " + str(total))
        i = i+1
        '''check, if the entry is already pre-saved'''
        if word in savedSynsets:
            #print("found already matched synset for: " + word)
            word_synset = wn.synset(savedSynsets[word])  # @UndefinedVariable
            synset_list.append( word_synset )
        else:
            word_synset = findSynsetInWordnet(word)
            if type(word_synset) == nltk.corpus.reader.wordnet.Synset:
                # print("cought it")
                synset_list.append( word_synset )
    return synset_list

def findSynsetInWordnet(word_string):
    ''' detects a propriate synset for a given word '''
    word_synsets = wn.synsets(word_string)  # @UndefinedVariable
    # print(word_synsets)
    word_synsets = selectOnlyN(word_synsets)
    if len(word_synsets) > 1 :
        ''' if there are more than one possible synset for a given word ... '''
        selectedSynset = displayDialog(word_string,word_synsets)
        writeEntryToFile([word_string,selectedSynset.name])
        return selectedSynset
        
    elif len(word_synsets) == 1 :
        return word_synsets[0]
    return manualEntry(word_string)

def readEntriesFromFile():
    data = {}
    datafile = os.path.dirname(sys.argv[0])+"/synsetdata.csv"
    inf = open(datafile, 'rb')
    reader = csv.reader(inf)
    for row in reader:
        if row:
            data[row[0]] = row[1]
    inf.close()
    return data

def writeEntryToFile(entry):
    datafile = os.path.dirname(sys.argv[0])+"/synsetdata.csv"
    #print(datafile)
    outf = open(datafile, 'a')
    writer = csv.writer(outf)
    writer.writerow(entry)
    outf.close()

def manualEntry(word_string):
    '''until a better solution is found, this always return None'''
    return None

def displayDialog(word_string, listOfSelections):
    ''' displays the selection dialog '''   
    def onselect():
        temp.text = int( listbox.curselection()[0] )
        master.destroy()
    def oncancle():
        temp.text = -1
        master.destroy()
    
    def center_window(w=300, h=200):
        # get screen width and height
        ws = master.winfo_screenwidth()
        hs = master.winfo_screenheight()
        # calculate position x, y
        x = (ws/2) - (w/2)    
        y = (hs/2) - (h/2)
        master.geometry('%dx%d+%d+%d' % (w, h, x, y))

    master = Tk()
    label = Label(master, text="Please select the appropriate meaning for the Attribute '" + word_string + "'.")
    temp = Label(master)
    listbox = Listbox(master, width=80, height=15)
    listbox.pack()
    for possibleSelection in listOfSelections:
        listbox.insert(END, possibleSelection.definition)
    listbox.bind('<<ListboxSelect>>')
    button = Button(master, text="OK", command=onselect)
    button2 = Button(master, text="CANCLE", command=oncancle)
    button.pack()
    button2.pack()
    label.pack()
    center_window(650, 320) 
    master.mainloop()
    if temp.text != -1:
        return listOfSelections[temp.text]
    else:
        return None

def getAttributes():
    '''reads a list of words from the database'''
    prettyprint("reading data from CouchDB...")
    wlist = []
    couch = couchdb.Server('http://gisforge.no-ip.org:5984/')
    db = couch['rwilb']
    result = db.view('test/test',group_level=1)
    for row in result:
        # print( str(row.key) + ' :  ' +  str(row.value) )
        wlist.append(row.key)
    print("WORDLIST.PY - " + "found " + str( len(wlist) ) + " unique Entries in the Database")
    return wlist

def getAttributesFromFile():
    '''reads attribues from a csv file'''
    data = set()
    #datafile = os.path.dirname(sys.argv[0])+"/amenities.csv"
    datafile = os.path.dirname(sys.argv[0])+"/landuse.csv"
    inf = open(datafile, 'rb')
    reader = csv.reader(inf)
    for row in reader:
        data.add(row[0])
    return list(data)

def getMaxFromList(liste):
    result = 0
    for entry in liste:
        if entry > result: result = entry
    return result

def assignToCategories(category_synsets,word_synsets):
    prettyprint("start assigning path_similarity...")
    assignedDict = {}
    for category in category_synsets:
        assignedDict[category] = []
    
    for word in word_synsets:
        tempValues = []
        for category in category_synsets:
            similarity = wn.path_similarity(word, category)
            #similarity = wn.lch_similarity(word, category)
            tempValues.append(similarity)
            #print("appended "+str(similarity)+" for "+str(category)+ " and "+str(word))
        #print("__________________________________")
        indexOfMaxValue = tempValues.index(getMaxFromList(tempValues))
        assignedDict[ category_synsets[ indexOfMaxValue ] ].append( word )
    return assignedDict

def assignToCategoriesLCH(category_synsets,word_synsets):
    prettyprint("start assigning lch_similarity...")
    assignedDict = {}
    for category in category_synsets:
        assignedDict[category] = []
    
    for word in word_synsets:
        tempValues = []
        for category in category_synsets:
            #similarity = wn.path_similarity(word, category)
            similarity = wn.lch_similarity(word, category)
            tempValues.append(similarity)
            #print("appended "+str(similarity)+" for "+str(category)+ " and "+str(word))
        #print("__________________________________")
        indexOfMaxValue = tempValues.index(getMaxFromList(tempValues))
        assignedDict[ category_synsets[ indexOfMaxValue ] ].append( word )
    return assignedDict

def calculateCategories(word_synsets):
    '''buildings all possible combinations as a set of sets to avoid duplicacy'''
    combinations = set()
    for subset in itertools.combinations(word_synsets,2):
        #subs = set()
        #subs.add(subset[0])
        #subs.add(subset[1])
        combinations.add(subset)
    combinations_list = list(combinations)
    '''now, making a list of lists out of the set of sets and add their similarity'''
    combinations_list_list = []
    for subset in combinations_list:
        subsetentry = []
        for subsubset in subset:
            subsetentry.append(subsubset)
        subsetsynset = str(wn.path_similarity(subsetentry[0], subsetentry[1]))
        subsetentry.append(subsetsynset)
        combinations_list_list.append((subsetentry))
        prettyprint(combinations_list_list)
    
    '''aggregate every similarity measure to its synset occurrence'''
    categories_similarity_dict = {}
    synsetcollection = {}
    for word_synset in word_synsets:
        categories_similarity_dict[word_synset] = []
    for word_synset in word_synsets:
        for entry in combinations_list_list:
            print(str(word_synset)+" in "+str(entry))
            if word_synset in entry:
                synsetcollection[word_synset] += float(entry[2])
    prettyprint(synsetcollection)
    #for entry in combinations_list_list:
    


    
    print(combinations_list_list)
    #for entry in combinations_list:
    #    combination = [ entry[0], entry[1] ]
    #    entry_synset = findSynsetsInWordnet(combination)

def printResultDict(indictionary):
    for entry in indictionary:
        print("______________\n"+entry.name+":\n_________________")
        entryindict = indictionary[entry]
        for subentry in entryindict:
            print(subentry.name)


if __name__ == '__main__':
    prettyprint("processing words ...")
    #word_list = getAttributesFromFile()
    #word_list = getAttributes()
    word_list = ['street','scrub','meadow','building','parking','swamp','desert','field','stream','lake','path']
    #word_list = ['street','scrub','meadow','building','parking','swamp']
    word_synsets = findSynsetsInWordnet(word_list)
    
    prettyprint("processing categories ...")
    #category_list = ["road","forest","water"]
    category_list = ["building","woods","water","field"]
    
    #category_list = ["necessity", "trivia"]
    """not really good results"""
    
    category_synsets = findSynsetsInWordnet(category_list)
    
    ###category_synsets = calculateCategories(word_synsets)
    
    #prettyprint(word_synsets)
    path_similarity = assignToCategories(category_synsets,word_synsets)
    #lch_similarity = assignToCategoriesLCH(category_synsets,word_synsets)
    print("Path-Similarity:")
    ##prettyprint(path_similarity)
    printResultDict(path_similarity)
    #print("LCH-Similarity:")
    #prettyprint(lch_similarity)
    #printResultDict(lch_similarity)
    # print( "main - " + str( findSynsetInWordnet("forest") ))
    
    #print(readEntriesFromFile())
    #print("eof")
