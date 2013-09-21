'''
Created on 01.08.2013

@author: scubbx
'''

from __future__ import print_function

def prettyprint (data):
    if type(data) == list:
        i = 0
        for dataentry in data:
            if type(dataentry) == list:
                print(str(i) + ':',end='  ')
                for datasubentry in dataentry:
                    if type(datasubentry) == float:
                        print( round(datasubentry,3), end=' , ')
                i += 1
                print()
            else:
                print( dataentry )
        print( ('-'*80) + "\nLength of Array: " + str(len(data)) )
    elif type(data) == dict:
        for dat in data:
            print(str(dat) + " :  " + str( data[dat]) )
        print( ('-'*80) + "\nLength of Dictionary: " + str(len(data)) )
    else:
        print("\n"+str(data))
        
    print(('-'*80) + '\n')