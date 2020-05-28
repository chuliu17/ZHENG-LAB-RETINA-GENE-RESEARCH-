#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb  6 14:17:30 2020

@author: audi
"""

# File:             geneMatch_original.py
# Author:           Akaash Venkat, Audi Liu



'''
Updates this quarter:
1.changed python 2 calls of dict.iteritems() to python3 d.items(). 
  Also changed these for the original file so that it can be run on python3. It's now called original.py.


2. Downloaded chromedriver and append its path in the PATH variable. 


3. put repititve code in modify_base_svg into functions:

A.  def update_dict(d_gene, dictionary, gene_info):
    
    #given a d_gene, and the D_A_1 (D TO A dictionary), update D_A_1 to have the correct gene mapping


B.  def store_pos(new_pos_dict, gene_list, A_D_final, D_B_PAIR, center_x, center_y):

    #calculate the position of the genes in a circle and store it into new_pos_dic
    #may need to add more arguments to customize the math parameters 

C.  def classify_once(INPUT, groups, groups_w): 

    #INPUT: genes that still need to be sorted
    #groups: the read-only copy groups
    #groups_w: the write-only copy of grouos. the gene is assigned to one of the groups in groups_w
    #classify_once traverses the genes in INPUT and places them into the correct group in groups_w based on the 
    #the gene's connection to the read-only groups
    

D. def classify(grous): 
   
    #basically calls classify_once repeatedly until all genes are grouped


Remarks:
I ran original.py just to test things out, and it turns out there are some genes in the gene list that's not in 
the text file, so it accessed the chrome web. I couldn't find another list on google drive though.

    
'''

from selenium import webdriver
from os.path import expanduser
import glob
import math
import random
import os
import subprocess
import sys
import time
import functools

from collections import defaultdict 



'''
all circle: the remaining stars become blue group a
top circle: remove all red stars from top circle, 
middle cirlce:  no need to hard code the star positions
'''

GENE_DATABASE_FILE = "info_files/gene_database.txt"
GENE_GROUP_FILE = "info_files/gene_group.txt"
UNIDENTIFIABLE_GENE_FILE = "info_files/unidentifiable_genes.txt"
CHANGED_NAME_GENE_FILE = "info_files/changed_name_genes.txt"

GENE_LIST = []  #All the genes in the database. format: a list of lists, the inner list has the gene game as the first elem and the second list the dict of gene to confidence level mapping
UNIDENTIFIABLE_LIST = []
CHANGED_NAME = {}
GROUP = {}
B_D_PAIR = {}



group1 = ["RPE65", "LRAT", "MERTK", "RBP3", "RGR"] #read-only
group2 = ["RHO", "PRPH2", "SAG", "CNGA1", "CNGB1", "FSCN2", "ROM1", "IMPG2", "PROM1"]
group3 = [ "RPGR", "RP1", "CLRN1", "MAK", "USH2A"] #removed BBSs because not in a_list
group4 = ["NR2E3", "CRX", "ZNF513", "PRPF31", "PRPF8", "PRPF3", "PRPF4", "PRPF6", "RP9", "SNRNP200", "DHX38"]

'''
groups = []
groups.append(group1)
groups.append(group2)
groups.append(group3)
groups.append(group4)
'''


blue = ["CYP8B1", "LRAT", "MERTK", "RGR", "RPE65"]
purple = ["FDFT1", "RBP3" ]
red = ["CYP51A1", "HSD17B7", "MSMO1", "SC5D", "RCVRN"]   

CYP8B1 = ["CH25H", "DHCR7", "FAXDC2", "FDFT1", "HSD17B7", "INS", "LSS", "MSMO1", "PPARA", "SC5D", "SQLE", "TM7SF2"]
LRAT = [ "ABCA4", "BEST1", "C2orf71", "C8orf37", "CERKL", "CLRN1", "CNGA1", "CNGB1", "CRB1", "CRX", "EYS", "FAM161A", 
          "FSCN2", "GUCA1B", "IDH3B", "IMPDH1", "IMPG2", "MERTK", "NR2E3", "NRL", "PDE6A", "PDE6B", "PDE6G", "PRCD", "PRPF3", 
          "PRPF31", "PRPH2", "RBP3", "RDH12", "RGR", "RHO", "RLBP1", "ROM1", "RP9", "RPE65", "RPGR", "SPATA7", "TOPORS", 
          "TULP1", "USH2A", "ZNF513"]
FDFT1 = ["ACAT1", "ACLY", "CH25H", "CYP51A1", "CYP8B1", "DECR1", "DHCR7", "DHDDS", "FAXDC2", "HSD17B7", "LSS", "MSMO1", "MVK",
         "PPARA", "RPE65", "SC5D", "SP1", "SQLE", "TM7SF2"]

MERTK = ["ABCA4", "BEST1", "C2orf71", "CERKL", "CLRN1", "CNGA1", "CNGB1", "CRB1", "CRX", "EYS", "FAM161A", "FSCN2", "GUCA1B", "IDH3B",
         "IMPDH1", "IMPG2", "KLHL7", "LRAT", "NR2E3", "PDE6A", "PDE6B", "PRCD", "PRPF31", "PRPH2", "RDH12", "RHO", "RLBP1", "ROM1",
         "RP9", "RPE65", "RPGR", "SNRNP200", "SPATA7", "TULP1", "USH2A", "ZNF513"]
RBP3 = ["ABCA4", "CRX", "GUCA1B", "LRAT", "NR2E3", "NRL", "PRCD", "PRPH2", "RCVRN", "RDH12", "RGR", "RHO", "RLBP1", "RPE65", "SAG", "TULP1", "ZNF513"]

RGR = ["ABCA4", "CERKL", "CNGA1", "CNGB1", "CRB1", "IDH3B", "LRAT", "NR2E3", "PDE6A", "PDE6B", "PRCD", "RBP3", "RDH12", "RHO", "RLBP1", "RPE65", "SAG", "TULP1"]

RPE65 =  ["ABCA4", "ALB", "BEST1", "C2orf71", "CERKL", "CLRN1", "CNGA1", "CNGB1", "CRB1", "CRX", "EYS", "FAM161A", "FDFT1", "FSCN2", "GUCA1B", "IDH3B", "IMPDH1", 
          "IMPG2", "KLHL7", "LRAT", "MERTK", "NR2E3", "NRL", "PDE6A", "PDE6B", "PDE6G", "PRCD", "PRPF3", "PRPF31", "PRPF8",
          "PRPH2", "RBP3", "RCVRN", "RDH12", "RGR", "RHO", "RLBP1", "ROM1", "RP1", "RP9", "RPGR", "SAG", "SNRNP200", "SPATA7",
          "TOPORS", "TULP1", "USH2A", "ZNF513"]

orange = CYP8B1 + LRAT + FDFT1+ MERTK + RBP3 + RGR + RPE65


orange = list(set(orange))


toremove = blue + purple + red

for gene in toremove:
    if gene in orange:
        orange.remove(gene)
        


REPLACED_STARS = red + purple + blue + orange
        
'''
GROUP1 =[]
GROUP2 = []
GROUP3 = []
GROUP4 = []
'''

        
    
def readDatabase():
    global GENE_LIST
    with open(GENE_DATABASE_FILE) as database_file:
        for line_content in database_file:
            if line_content != "\n":
                gene_info = []
                line_content = line_content.replace(" ", "")
                line_content = line_content.replace(")", "")
                line_content = line_content.replace("\n", "")
                temp_list = line_content.split("-",1)
                main_gene = temp_list[0]
                connecting_genes_list = temp_list[1].split(",")
                neighbors = {}
                for connecting_gene in connecting_genes_list:
                    name = connecting_gene.split("(")[0] 
                    num = float(connecting_gene.split("(")[1])
                    neighbors[name] = num
                gene_info.append(main_gene)
                gene_info.append(neighbors)
                GENE_LIST.append(gene_info) # a list of lists
    database_file.close()


def readUnidentifiable():
    with open(UNIDENTIFIABLE_GENE_FILE) as unidentifiable_file:
        for line_content in unidentifiable_file:
            line_content = line_content.replace(" ", "")
            line_content = line_content.replace("\n", "")
            if line_content != "" and "followinggenescannotbefound" not in line_content:
                UNIDENTIFIABLE_LIST.append(line_content)
    unidentifiable_file.close()


def readChangedName():
    with open(CHANGED_NAME_GENE_FILE) as changed_name_file:
        for line_content in changed_name_file:
            line_content = line_content.replace(" ", "")
            line_content = line_content.replace("\n", "")
            if line_content != "" and "followinggeneshavebeenrenamed" not in line_content:
                orig_name = line_content.split("=>")[0]
                new_name = line_content.split("=>")[1]
                CHANGED_NAME[orig_name] = new_name
    changed_name_file.close()


def writeToDatabase(): ##not so efficient here because writing the entire file over and over again. since it's called inside a for loop in parseinput, we can make this only write the last element of GENE_LIST
    os.system('rm ' + GENE_DATABASE_FILE)
    os.system('touch ' + GENE_DATABASE_FILE)
    database_file = open(GENE_DATABASE_FILE, "w")
    for counter in range(0, len(GENE_LIST)):
        gene_info = GENE_LIST[counter]
        main_gene = gene_info[0]
        connecting_genes_list = gene_info[1]
        line_content = main_gene + " - "
        for key, value in sorted(connecting_genes_list.items() ):
            line_content = line_content + key + "(" + str(value) + "), " 
        line_content = line_content[:-2]
        database_file.write(line_content + "\n\n")
    database_file.close()


def writeGeneGroups():
    os.system('touch ' + GENE_GROUP_FILE)
    grouping_file = open(GENE_GROUP_FILE, "w")

    groups = ["A", "B", "C", "D"]
    descriptions = ["Input gene that has direct connection with another input gene", "Input gene that is indirectly connected to another input gene, via an intermediate gene", "Input gene that is not directly or indirectly connected to another input gene", "Intermediate gene that connects Group B genes with Group A or other Group B genes"]

    for counter in range(0, len(groups)):
        group_id = groups[counter]
        description = descriptions[counter]
        grouping_file.write("Group " + group_id + ": " + description + "\n")
        grouping_file.write("---\n")
        cluster = getListForGroup(group_id)
        for gene in cluster:
            grouping_file.write(gene + "\n")
        grouping_file.write("\n\n\n")

    grouping_file.close()


def writeUnidentifiable():
    os.system('touch ' + UNIDENTIFIABLE_GENE_FILE)
    cleaned_unidentifiable_list = []
    for gene in UNIDENTIFIABLE_LIST:
        if gene not in cleaned_unidentifiable_list:
            cleaned_unidentifiable_list.append(gene)
    if len(cleaned_unidentifiable_list) != 0:
        unidentifiable_file = open(UNIDENTIFIABLE_GENE_FILE, "w")
        unidentifiable_file.write("The following genes cannot be found on the online STRING database, and will not be used in this program:\n\n")
        for gene in cleaned_unidentifiable_list:
            unidentifiable_file.write(gene + "\n")
        unidentifiable_file.close()
    else:
        os.system('rm ' + UNIDENTIFIABLE_GENE_FILE)


def writeChangedName():
    os.system('touch ' + CHANGED_NAME_GENE_FILE)
    if not CHANGED_NAME:
        os.system('rm ' + CHANGED_NAME_GENE_FILE)
    else:
        changed_name_file = open(CHANGED_NAME_GENE_FILE, "w")
        changed_name_file.write("The following genes have been renamed, as per the online STRING database:\n\n")
        for key, value in CHANGED_NAME.items():
            changed_name_file.write(key + " => " + value + "\n")
        changed_name_file.close()


def initialize_connections():
    for gene_info in GENE_LIST:
        gene = gene_info[0]
        GROUP[gene] = "C"


def identifyGroupA(gene_list):
    for i in range(0, len(gene_list)):
        gene = gene_list[i][0]
        gene_neighbors = gene_list[i][1]
        
        for j in range(0, len(gene_list)):
            if i == j:
                continue
            
            other_gene = gene_list[j][0]
            
            if other_gene in gene_neighbors.keys():
                GROUP[gene] = "A"


def identifyGroupB(gene_list):#
    for i in range(0, len(gene_list)):
        
        content_list = []
        gene = gene_list[i][0]
        gene_neighbors = gene_list[i][1]
        
        
        if GROUP[gene] == "A":
            continue
        
        for j in range(0, len(gene_list)):
            if i == j:
                continue

            other_gene = gene_list[j][0]
            other_gene_neighbors = gene_list[j][1]

            for inter_gene in gene_neighbors.keys():
                if inter_gene in other_gene_neighbors.keys():
                    if gene_neighbors[inter_gene] > other_gene_neighbors[inter_gene]:
                        content_list.append([other_gene_neighbors[inter_gene], inter_gene, other_gene])
                    else:
                        content_list.append([gene_neighbors[inter_gene], inter_gene, other_gene]) #confidence level,  d gene, and A or B gene
                                             
        best_match = max(content_list)
        #print(best_match)
        
        if GROUP[gene] == "C":
            GROUP[gene] = "B"
            GROUP[best_match[1]] = "D" #intermediate
            B_D_PAIR[gene] = best_match[1]
            
        
                 


def parseInput():
    os.system('clear')
    arg = ""
    content = []
    input_genes = []
    input_list = []
    if (len(sys.argv) == 1):
        print("Please try running program again, this time adding an argument.")
        sys.exit(0)
    else:
        arg = sys.argv[1]
    if (arg[-4:] == '.txt'): #checking the file extensions
        with open(arg) as arg_input:
            content = arg_input.readlines()
    else:
        print("Please try running program again, this time passing in an argument of type '.txt'")
        sys.exit(0)

    for gene in content:
        input_list.append(gene.replace(" ", "").replace("\n", ""))

    for gene in input_list:
        if gene not in input_genes:
            input_genes.append(gene)

    current_gene_list = GENE_LIST

    for gene in input_genes:
        already_present = False
        for iter in range(0, len(current_gene_list)):
            existing_gene = current_gene_list[iter][0]
            if existing_gene == gene:
                already_present = True
                break

        if already_present == False:
            
            if gene in CHANGED_NAME:
                break
            if gene in UNIDENTIFIABLE_LIST:
                break
            
            gene_info = []
            gene_neighbors = find_neighbor(gene)

            if gene_neighbors == -1:
                UNIDENTIFIABLE_LIST.append(gene)
            else:
                if isinstance(gene_neighbors, str):
                    correct_gene = gene_neighbors
                    CHANGED_NAME[gene] = correct_gene
                    gene = correct_gene
                    gene_neighbors = find_neighbor(gene)

                gene_info.append(gene)
                if "" in gene_neighbors:
                    time.sleep(1)
                    gene_info.append(find_neighbor(gene))
                else:
                    gene_info.append(gene_neighbors)
                GENE_LIST.append(gene_info)
        GENE_LIST.sort()
        writeToDatabase() 

    initialize_connections()
    identifyGroupA(GENE_LIST)
    identifyGroupB(GENE_LIST)



def getListForGroup(group_id):
    cluster = []
    for gene in GROUP:
        if GROUP[gene] == group_id:
            cluster.append(gene)
    return cluster



def find_neighbor(input_gene):
    gene_connectors = {}
    driver = webdriver.Chrome()
    driver.get("http://string-db.org/")
    driver.find_element_by_id("search").click()
    driver.find_element_by_id("primary_input:single_identifier").send_keys(input_gene)
    driver.find_element_by_id("species_text_single_identifier").send_keys("Homo sapiens")
    driver.find_element_by_xpath("//*[@id='input_form_single_identifier']/div[4]/a").click()
    if "Sorry, STRING did not find a protein" in driver.page_source:
        return -1
    if "Please select one from the list below" in driver.page_source:
        driver.find_element_by_xpath("//*[@id='proceed_form']/div[1]/div/div[2]/a[2]").click()
    driver.find_element_by_id("bottom_page_selector_settings").click()
    driver.find_element_by_xpath("//*[@id='bottom_page_selector_legend']").click()
    page_data = driver.page_source
    split1 = page_data.split("<td class=\"td_name middle_row first_row last_row\" onclick=")
    split2 = split1[1].split("</td>")
    split3 = split2[0].split("\">")
    correct_gene_name = split3[1]
    if input_gene != correct_gene_name: #if a string is returned rather than a list, then run it again where find_neighbor is called
        return str(correct_gene_name)
    driver.find_element_by_xpath("//*[@id='bottom_page_selector_table']").click()
    driver.find_element_by_id("bottom_page_selector_settings").click() #click settings
    driver.find_element_by_xpath("//*[@id='standard_parameters']/div/div[1]/div[3]/div[2]/div[2]/div[1]/label").click()
    driver.find_element_by_xpath("//select[@name='limit']/option[text()='custom value']").click()
    driver.find_element_by_id("custom_limit_input").clear()
    driver.find_element_by_id("custom_limit_input").send_keys("500")
    time.sleep(5)
    driver.find_element_by_xpath("//*[@id='standard_parameters']/div/div[1]/div[5]/a").click()
    time.sleep(10)
    driver.find_element_by_id("bottom_page_selector_table").click()
    driver.find_element_by_xpath("//*[@id='bottom_page_selector_legend']").click()
    connectors = driver.find_elements_by_class_name("linked_item_row")
    for connector in connectors:
        neighbor = str(connector.text.split(' ')[0].split('\n')[0])
        confidence_value = str(connector.text.split(' ')[-1].split('\n')[-1])
        gene_connectors[neighbor] = float(confidence_value)
    return gene_connectors



def download_svg(gene_list):

    if len(gene_list) < 2:
        return -1
    
    SVG_STRING = ""
    for gene in gene_list:
        SVG_STRING = SVG_STRING + gene + "\n"
    
    driver = webdriver.Chrome()
    driver.get("http://string-db.org/")
    driver.find_element_by_id("search").click()
    driver.find_element_by_id("multiple_identifiers").click()
    driver.find_element_by_id("primary_input:multiple_identifiers").send_keys(SVG_STRING)
    driver.find_element_by_id("species_text_multiple_identifiers").send_keys("Homo sapiens")
    driver.find_element_by_xpath("//*[@id='input_form_multiple_identifiers']/div[5]/a").click()
    time.sleep(5)
    if "The following proteins in" in driver.page_source and "appear to match your input" in driver.page_source:
        driver.find_element_by_xpath("//*[@id='proceed_form']/div[1]/div/div[2]/a[2]").click()
    time.sleep(20)
    driver.find_element_by_id("bottom_page_selector_table").click()
    time.sleep(5)
    driver.find_element_by_id("bottom_page_selector_settings").click()
    time.sleep(15)
    driver.find_element_by_id("confidence").send_keys(" ")
    time.sleep(10)
    driver.find_element_by_id("block_structures").send_keys(" ")
    time.sleep(10)
    driver.find_element_by_xpath("//*[@id='standard_parameters']/div/div[1]/div[5]/a").click()
    time.sleep(15)
    driver.find_element_by_xpath("//*[@id='bottom_page_selector_legend']").click()
    time.sleep(10)
    driver.find_element_by_id("bottom_page_selector_table").click()
    time.sleep(25)
    driver.find_element_by_xpath("//*[@id='bottom_page_selector_table_container']/div/div[2]/div/div[3]/div[2]/a").click()
    time.sleep(10)

    terminal_output = subprocess.Popen(['pwd'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = terminal_output.communicate()
    pwd = stdout[:-1]
    downloads_dir = expanduser("~") + '/Downloads/*'
    downloaded_files = glob.glob(expanduser("~") + '/Downloads/*')
    recent_file = max(downloaded_files, key=os.path.getctime)
    move_command = 'mv "' + recent_file + '" "' + pwd + '/svg_files/_base.svg"'
    os.system(move_command)




def getGene(str):
    lst1 = str.split('>')
    lst2 = lst1[1].split('<')
    return lst2[0]



def writeToFile(content, file_name):
    os.system('touch ' + file_name)
    os.system('rm ' + file_name)
    os.system('touch ' + file_name)
    file = open(file_name, "w")
    for counter in range(0, len(content)):
        file.write(str(content[counter]))
    file.close()


"""
    New Idea for Tripod of A's:
    "Hardcode" positions for 3 main genes (ABCA4, RPE65, RHO)
    Split area into 3 zones and use the random generating in each zone
    Venn Diagram into 7 parts (A, B, C, AB, BC, AC, ABC)
        3 extra loser zones
        3 extra zones for the main ones (increase radius maybe, change color maybe)
"""


def classify(groups): 
    groups_w = groups[:] #groups_w is write only 
    
    group1 = groups[0][:] #need to copy because we do not want to modify the original groups method 
    group2 = groups[1][:]
    group3 = groups[2][:]
    group4 = groups[3][:]
    
    
    a_list = getListForGroup("A")
    
    
   # print("before:")
   # print(a_list)
    for gene in group1:
        if gene in a_list:
            a_list.remove(gene)
    
    for gene in group2:
        if gene in a_list:
            a_list.remove(gene)
            
    for gene in group3:
        if gene in a_list:
            a_list.remove(gene)
            
    for gene in group4:
        if gene in a_list:
            a_list.remove(gene)
            
    next_input = a_list
    
    #print("after:")
    #print(next_input)
    
    while next_input != []: #while there are still loners that are not grouped
        print("before:")
        print(groups_w[0])
        next_input = classify_once(next_input, groups, groups_w)
        print("after:")
        print(groups_w[0])
        group1 = groups_w[0][:]
        group2 = groups_w[0][:]
        group3 = groups_w[0][:]
        group4 = groups_w[0][:]
    
    return groups_w
    
    
#INPUT: genes that still need to be sorted
#groups: the read-only copy groups
#groups_w: the write-only copy of grouos. the gene is assigned to one of the groups in groups_w
#classify_once traverses the genes in INPUT and places them into the correct group in groups_w based on the 
#the gene's connection to the read-only groups
def classify_once(INPUT, groups, groups_w): 
    #group1-4 read only, GROUP 1-4 write only
    loners = []
    '''
    print(GENE_LIST[0][0])
    l = GENE_LIST[0][1].keys()
    l.sort()
    print(l)
    '''
    "ACLY"
    group1_r = groups[0]
    group2_r = groups[1]
    group3_r = groups[2]
    group4_r = groups[3]


    
    
    for a_gene in INPUT: #circle_group #GENE_LIST: a list of lists, each innerr list has two items: the main gene name and a dictionary of name to confidence level
        for i in range(0, len(GENE_LIST)):
            if str(a_gene) == str(GENE_LIST[i][0]):
                count = [0 for j in range(4)] #list of counts of connections in g1,g2,g3,g4
                confidence_level = [0 for k in range(4)]
                #l = GENE_LIST[i][1].keys()
                #l.sort()
                for gene, confidence in GENE_LIST[i][1].items():
                    #print(gene)
                    if gene in group1_r:
                        count[0] += 1
                        confidence_level[0] += confidence
                    elif gene in group2_r:
                        count[1] += 1
                        confidence_level[1] += confidence
                    elif gene in group3_r:
                        count[2] += 1
                        confidence_level[2] += confidence
                    elif gene in group4_r:
                        count[3] += 1
                        confidence_level[3] += confidence
                      
                
                #print("a_gene is")
                #print(a_gene)
            
                    
                #print(count)
                max_count = max(count)
                max_index = [a for a, b in enumerate(count) if b == max_count]
                #print("number of max items is")
                #print(len(max_index))
            
                
                if count == [ 0 for num in range(4) ]:# no connections at all
                    loners.append(a_gene)
                    
                elif len(max_index) == 1:
                    if max_index[0] == 0:
                        groups_w[0].append(a_gene)
                    elif max_index[0] == 1:
                        groups_w[1].append(a_gene)
                    elif max_index[0] == 2:
                        groups_w[2].append(a_gene)
                    elif max_index[0] == 3:
                        groups_w[3].append(a_gene)    
                        
                else: #use confidence level to compare
                    #print("max_index")
                    #print(max_index)
                    
                 
                    finalists = [confidence_level[n] for n in  max_index ]
                    
                    #print("conf level")
                    #print(finalists)
                    
                    max_conf = max(finalists)
                    index =  [a for a, b in enumerate(finalists) if b == max_conf]#index with the maximumn conf value
                    #print("max conf index")
                    #print(index)
                    #print("\n")
                    group_num = max_index[index[0]] #if there's a confidence level tie, then just do random. We just choose the first index we find then.
                    
                    if group_num == 0:
                        groups_w[0].append(a_gene)
                    elif group_num == 1:
                        groups_w[1].append(a_gene)
                    elif group_num == 2:
                        groups_w[2].append(a_gene)
                    elif group_num == 3:
                        groups_w[3].append(a_gene)  
    '''
    print(len(INPUT))
    
    print("GROUP1: " + str(len(GROUP1)) )
    print("GROUP2: " + str(len(GROUP2)) )
    print("GROUP3: " + str(len(GROUP3)) )
    print("GROUP4: " + str(len(GROUP4)) )
    print("LONER: " + str(len(LONER)) )
    #print(LONER)
    '''
    return loners

    
    '''
    print(GROUP1)
    print(GROUP2)
    print(GROUP3)
    print(GROUP4)
    print(LONER)
    '''    
                        

#given a d_gene, and the D_A_1 (D TO A dictionary), update D_A_1 to have the correct gene mapping
def update_dict(d_gene, dictionary, gene_info):
     dictionary[d_gene][0] += 1          
     if gene_info[1][d_gene] >  dictionary[d_gene][2]: #if confidence level of new d_gene  is greater than the current in the dictionary database
         dictionary[d_gene][2] = gene_info[1][d_gene] #replace with the bigger confidence level
         dictionary[d_gene][1] = gene_info[0] 
    


#calculate the position of the genes in a circle and store it into new_pos_dic
#1.12, 1.2 and 1.07 are arbitrary and maybe needs to be passed in
def store_pos(new_pos_dict, gene_list, A_D_final, D_B_PAIR, center_x, center_y):
    radius = len(gene_list) * 14 #14 is a hard coded number 
    for i in range(len(gene_list)): #size 7
        x = int(round(center_x  + radius * math.cos(6.28/len(gene_list)*i) ))
        y = int(round(center_y + radius * math.sin(6.28/len(gene_list)*i) ))
        new_pos_dict[gene_list[i]] = [ str(x), str(y) ]
        '''
        else: #if they're a star, need special code to generate the stars
            star_code = draw_star_text(x,y, gene_list[i]) #UPDATE 1: Insert star_cpde when making the cirlce
            length = len(content)
            content.insert(length-1, star_code)
        '''
        
        if gene_list[i] in A_D_final.keys(): #storing the d_gene location
            d_gene_per_a = len(A_D_final[gene_list[i]])
            if d_gene_per_a == 1: #there are only one d_gene matched to the a_gene
                d_gene = A_D_final[gene_list[i]][0]
                radius_d = radius * 1.12
                d_x = int(round(center_x  + radius_d * math.cos(6.28/len(gene_list)*i) ))
                d_y = int(round(center_y + radius_d * math.sin(6.28/len(gene_list)*i) ))
                new_pos_dict[d_gene] = [ str(d_x), str(d_y) ]
                #print(d_gene +" G1 modified!")
                
                b_gene = D_B_PAIR[d_gene]
                radius_d = radius_d * 1.07
                b_x = int(round(center_x  + radius_d * math.cos(6.28/len(gene_list)*i) ))
                b_y = int(round(center_y + radius_d * math.sin(6.28/len(gene_list)*i) ))
                new_pos_dict[b_gene] = [ str(b_x), str(b_y) ]
            
            elif d_gene_per_a > 1:# there are multiple b_genes matched to one a_gene
                angle_1 = i - 1.001/d_gene_per_a #make the d_gene come out from the a_gene at an angle.
                for k in range(d_gene_per_a):
                    angle = angle_1 + k * 1.001/(d_gene_per_a -1)
                    d_gene = A_D_final[gene_list[i]][k]
                    radius_d = radius * 1.2
                    
                    d_x = int(round(center_x + radius_d * math.cos(6.28/len(gene_list)*angle) ))
                    d_y = int(round(center_y + radius_d * math.sin(6.28/len(gene_list)*angle) ))
                    new_pos_dict[d_gene] = [ str(d_x), str(d_y) ]
                    #print(d_gene +" G2 modified!")
                    
                    b_gene = D_B_PAIR[d_gene]
                    radius_d = radius_d * 1.07
                    b_x = int(round(center_x + radius_d * math.cos(6.28/len(gene_list)*angle) ))
                    b_y = int(round(center_y+ radius_d * math.sin(6.28/len(gene_list)*angle) ))
                    new_pos_dict[b_gene] = [ str(b_x), str(b_y) ]
    
        

def modify_base_svg(groups_expanded):   #450 lines long lmao     
    grey = "(217,217,217)"
    yellow = "(255,255,0)"
    red = "(255,0,0)"
    green = "(0,153,0)"
    blue = "(52,152,219)"

    
    with open("svg_files/_base.svg") as base:
        content = base.readlines()

    content[0] = "<svg class=\"notselectable\" height=\"5800\" id=\"svg_network_image\" width=\"3500\" xmlns=\"http://www.w3.org/2000/svg\" xmlns:svg=\"http://www.w3.org/2000/svg\" xmlns:xlink=\"http://www.w3.org/1999/xlink\">"

    height = 5800
    width = 3500 #

    old_pos_dict = {}
    
    new_pos_dict = {} #key: string name of gene, value: [str(b_x), str(b_y)]
    
    
    
    # CODE TO DETERMINE WHICH A GENE SHOULD BE MAPPED TO WHAT D GENE 
    GROUP1 = groups_expanded[0]
    print("INITIAL:")
    print(GROUP1)
    GROUP2 = groups_expanded[1]
    GROUP3 = groups_expanded[2]
    GROUP4 = groups_expanded[3]
    
    
    d_list = getListForGroup("D")
    #print("d_list:")
    #print(d_list)
    a_list = getListForGroup("A")
    
    
    D_A_1 = {}
    D_A_2 = {}
    D_A_3 = {}
    D_A_4 = {}
    for d_gene in d_list: #number of genes that the d_gene are connected to group1, a_gene, confidence level ]
         D_A_1[d_gene] = [0, "", 0.0]  
         D_A_2[d_gene] = [0, "", 0.0]
         D_A_3[d_gene] = [0, "", 0.0]
         D_A_4[d_gene] = [0, "", 0.0]
    
    #print(GENE_LIST[0])
    for i in range(len(GENE_LIST)):
        gene_info = GENE_LIST[i]
        a_gene = gene_info[0] #a gene name. GENE_LIST[i][1] is the dictionary of connections 
        genes = gene_info[1].keys()
        for d_gene in d_list:
            if d_gene in genes:
                if a_gene in GROUP1:
                    update_dict(d_gene, D_A_1, gene_info) 
                elif a_gene in GROUP2:
                    update_dict(d_gene, D_A_2, gene_info)
                elif a_gene in GROUP3:
                    update_dict(d_gene, D_A_3, gene_info)
                elif a_gene in GROUP4:
                    update_dict(d_gene, D_A_4, gene_info)
                                   
                              
    #print(D_A_1)
    #print(D_A_2)
    #print(D_A_3)
    #print(D_A_4)
    
    A_D_final = {} #the dictionary that maps which A gene should the D gene be placed to on the graph
    #we first determine what circle the D gene should belong to, then we compare what A gene in the circle
    #does the d gene have the highest confidence level with
    for a_gene in a_list:
        A_D_final[a_gene] = []
    
    dict_list = []
    dict_list.append(D_A_1)
    dict_list.append(D_A_2)
    dict_list.append(D_A_3)
    dict_list.append(D_A_4)
    for d_gene in d_list:
        counts = [dic[d_gene][0] for dic in dict_list] # list of counts for group 1 thru 4
        max_count = max(counts)
        max_index = [a for a, b in enumerate(counts) if b == max_count]
        
        if len(max_index) == 1: #only one maximum value among 4 groups
            a_gene = dict_list[max_index [0] ][d_gene] [1]
            # a to a list of d_genes
            A_D_final[a_gene].append(d_gene)
            
        else:
            dict_list_final = [dict_list[k] for k in max_index]
            confidence_levels = [dic[d_gene][2] for dic in dict_list_final ]# the confidence levels of the finalists
            max_conf = max(confidence_levels)
            index =  [a for a, b in enumerate(confidence_levels) if b == max_conf]
            group_num = max_index[index[0]] #groupnum = 0 1 2 or 3
            
            a_gene = dict_list[group_num][d_gene][1]#dict_list[group_num][d_gene] is something like [1, 'FDFT1', 0.4]
            A_D_final[a_gene].append(d_gene)
    
    
    ################################
    #print(len(A_D_final))
    #print(A_D_final.values())
    '''
    for key,val in A_D_final.items():
        if val != []:
            print(key)
            print(val)
    '''
    
    #CALCULATING WHAT NODES ARE STARS
    
    '''
    FDFT1 - NSDHL, SC5D, MSMO1, HSD17B7, CYP51A1, C14orf1, R3HDM4, AGMO, SYVN1	
    CYP8B1 - TACSTD2, PRPF19
    RPE65 - CCT6B, MYO7A
    LRAT - BLCAP
    MERTK - VAV1, GRB2
    RBP3 - E2F2, HR, RCVRN 
    RGR -
    '''
    
    
    potential_stars = [ "NSDHL", "SC5D", "MSMO1", "HSD17B7", "CYP51A1", "C14orf1", "R3HDM4", "AGMO", "SYVN1", "TACSTD2", "PRPF19", "CCT6B", "MYO7A", "BLCAP", "VAV1", "GRB2" ,"E2F2", "HR", "RCVRN"]
    group1_ = []
    group2_ = []
    group3_ = []
    group4_ = []
    
    #RBP3 and FDFT1 are in 7 cirlce
    
    
    
    for gene in potential_stars:
        if gene in GROUP1:
            group1_.append(gene)
        elif gene in GROUP2:
            group2_.append(gene)
        elif gene in GROUP3:
            group3_.append(gene)
        elif gene in GROUP4:
            group4_.append(gene)
    '''
            
    print("GROUP1_STARS:") #7
    print(group1_)
    
    print("GROUP2_STARS:") #78
    print(group2_)
            
    print("GROUP3_STARS:") #15
    print(group3_)
            
    print("GROUP4_STARS:") #49
    print(group4_)
    '''
    # 7 to be replaced,
    # 5 to be added
    ADDED_STARS = group1_ + group2_ + group3_ + group4_ #['SC5D', 'MSMO1', 'HSD17B7', 'CYP51A1', 'RCVRN'] #red stars
    
    #REPLACED_STARS = ADDED_STARS (red) + ...
    #REPLACED_STARS =  red + blue + purple + orange
    
    #ADDING THE TWO NEW STARS INTO
    
    
    
    
    
    ###############################
    #Making the nodes form a cirlce 
    GROUP1 = GROUP1 + ADDED_STARS
    print("AFTER ADDING")
    print(GROUP1)
    
    radius_1 = len(GROUP1) * 14 #
    center_x =  1750
    center_y =  400
    
    #code that adds the svg lines into the file first, location can be random since we'll fix it here.
    
    #GROUP1.append("RBP3") 
    #GROUP1.append("FDFT1")
    
   
    D_B_PAIR = {v : k for k, v in B_D_PAIR.items()} #reverse the key and value
    
    
    #Hard coding that changes the orders ot the nodes in GROUP1 to make the diagrom look better
    print(GROUP1)
    GROUP1.remove("RBP3")
    length = len(GROUP1)
    GROUP1.insert(2,"RBP3")
    
    GROUP1.remove("FDFT1")
    GROUP1.insert(4,"FDFT1")
    
    
    store_pos(new_pos_dict, GROUP1, A_D_final, D_B_PAIR, 1750, 400)
    store_pos(new_pos_dict, GROUP2, A_D_final, D_B_PAIR, 1750, 2000)
    store_pos(new_pos_dict, GROUP3, A_D_final, D_B_PAIR, 1750, 3600)
    store_pos(new_pos_dict, GROUP4, A_D_final, D_B_PAIR, 1750, 4700)



    
    #HERE WE CHANG THE LOCATION OF THE A GENES TO BE IN CICRLES. CHANGE THE LOCATION OF THE D GENES TOO

    
    '''
    for k in range(len(GROUP2)):
        if GROUP2[k] == "EMC1":
            print(k)
    '''
    
    
    GROUP2.remove("EMC1")
    GROUP2.append("EMC1")
    
    GROUP2.remove("ALB")
    
    GROUP2.insert(51,"ALB")
    
    
    
    center_y = 2000
    
    #This code is to make the green genes line up on the right
    #print(GROUP2)
    GROUP2.remove("ENO4")
    GROUP2.remove("ALB")
    GROUP2.remove("NEK2")
    GROUP2.remove("AKT1")
    GROUP2.remove("STAT3")
    GROUP2.remove("PDE6A")
    GROUP2.remove("GAPDH")
    GROUP2.remove("RHO")

    
    GROUP2.insert(len(GROUP2)-1,"ALB" )
    GROUP2.insert(len(GROUP2)-1,"ENO4" )
    GROUP2.insert(len(GROUP2)-1,"NEK2" )
    GROUP2.insert(len(GROUP2)-1,"AKT1" )
    GROUP2.insert(len(GROUP2)-1,"RHO" )
    GROUP2.insert(len(GROUP2)-1,"PDE6A" )
    GROUP2.insert(len(GROUP2)-1,"GAPDH" )
    GROUP2.insert(len(GROUP2)-1,"STAT3" )
    
    
    
    
    GROUP2.remove("RCVRN")
    GROUP2.remove("SC5D")
    GROUP2.remove("MSMO1")
    GROUP2.remove("HSD17B7")
    GROUP2.remove("CYP51A1")


    
    GROUP2.insert(len(GROUP2)-16,"SC5D" )
    GROUP2.insert(len(GROUP2)-16,"MSMO1" )
    GROUP2.insert(len(GROUP2)-16,"HSD17B7" )
    GROUP2.insert(len(GROUP2)-16,"CYP51A1" )
    GROUP2.insert(len(GROUP2)-16,"RCVRN")
    
    #change the order of the red for both circles, fix radius,
    #make sure the swap for the green gene to be at the right pos worked

   
    
    
        

    
    #change locations of the nodes: i.e. change the content of text file 
    for i in range(len(content)): #change color, delete ellipses, and initialize old_pos_dict
        gene_name = ""
        
        if "ellipse cx=" in content[i]:
            content[i] = ""
        
        if "circle class" in content[i]:
            
            gene_name = getGene(content[i+3])
            rgb_val = content[i].split("rgb")[1].split('"')[0]
            position_data = content[i].split("cx=")[1].split(" display")[0].replace("cy=", "").replace("\"", "")
            old_pos_dict[position_data] = gene_name #initialize old_pos_dict
            
            #if gene_name == "ABCA4" or gene_name == "RPE65" or gene_name == "RHO":
             #   content[i] = content[i].replace(rgb_val, blue)
                
            if GROUP[gene_name] == "A":
                content[i] = content[i].replace(rgb_val, blue)
            elif GROUP[gene_name] == "B":
                content[i] = content[i].replace(rgb_val, yellow)
            elif GROUP[gene_name] == "C":
                content[i] = content[i].replace(rgb_val, red)
            elif GROUP[gene_name] == "D":
                content[i] = content[i].replace(rgb_val, green)

    a_list = getListForGroup("A")
    b_list = getListForGroup("B")
    c_list = getListForGroup("C")
    d_list = getListForGroup("D")
    


    base_b_y = int(height / 6)
    lowest_d_y = 0
   
     

    #actually changing the content in the file 
    for i in range(len(content)):            
        if "line class=\"nw_edge\"" in content[i] and ".0\" stroke=" in content[i]:
            content[i] = ""
        
        
        if "line class=\"nw_edge\"" in content[i] and ((".1\" stroke=" in content[i]) or (".2\" stroke=" in content[i])): #updating the edge pos
            old_width = float(content[i].split("stroke-width=\"")[1].split("\"")[0])
            old_opacity = float(content[i].split("stroke-opacity=\"")[1].split("\"")[0])
            new_width = str(0.50 * old_width)
            new_opacity = str(0.50 * old_opacity)

            
            
            old_x1 = content[i].split("x1=\"")[1].split("\"")[0]
            old_y1 = content[i].split("y1=\"")[1].split("\"")[0]
            old_x2 = content[i].split("x2=\"")[1].split("\"")[0]
            old_y2 = content[i].split("y2=\"")[1].split("\"")[0]
            
            mod_old_x1 = str(float(old_x1) - 0.5)
            mod_old_x2 = str(float(old_x2) - 0.5)
            mod_old_y1 = str(float(old_y1) - 0.5)
            mod_old_y2 = str(float(old_y2) - 0.5)
            
            if ".0" in mod_old_x1:
                mod_old_x1 = mod_old_x1[:-2]
            if ".0" in mod_old_x2:
                mod_old_x2 = mod_old_x2[:-2]
            if ".0" in mod_old_y1:
                mod_old_y1 = mod_old_y1[:-2]
            if ".0" in mod_old_y2:
                mod_old_y2 = mod_old_y2[:-2]
            
            gene1_name = old_pos_dict[str(mod_old_x1) + " " + str(mod_old_y1)]
            gene2_name = old_pos_dict[str(mod_old_x2) + " " + str(mod_old_y2)]
           
    
            if gene1_name in new_pos_dict and gene2_name in new_pos_dict: 
                new_pos1 = new_pos_dict[gene1_name]
                new_pos2 = new_pos_dict[gene2_name]
                updated_new_pos1 = [str(float(new_pos1[0]) + 0.5), str(float(new_pos1[1]) + 0.5)]
                updated_new_pos2 = [str(float(new_pos2[0]) + 0.5), str(float(new_pos2[1]) + 0.5)]
                first_half = content[i].split("stroke-opacity=\"")[0]
                #second_half = content[i].split("/>")[1]
                content[i] = first_half + "stroke-opacity=\"" + new_opacity + "\" stroke-width=\"" + new_width + "\" style=\"\""  +" x1=\"" + updated_new_pos1[0] + "\" y1=\"" + updated_new_pos1[1] + "\" x2=\"" + updated_new_pos2[0] + "\" y2=\"" + updated_new_pos2[1] + "\" />" + "\n"
                
        
        if "<circle cx" in content[i]: #update the node pos
            old_x = content[i].split("cx=\"")[1].split("\"")[0]
            old_y = content[i].split("cy=\"")[1].split("\"")[0]
            gene_name = old_pos_dict[str(old_x) + " " + str(old_y)]
            if gene_name in new_pos_dict:
                new_pos = new_pos_dict[gene_name]
                first_half = content[i].split(" cx=")[0]
                second_half = content[i].split("fill=")[1]
                content[i] = first_half + " cx=\"" + new_pos[0] + "\" cy=\"" + new_pos[1] + "\" fill=" + second_half
        
        if "<circle class" in content[i]: #update the node pos too, need to change multiple places
            old_x = content[i].split("cx=\"")[1].split("\"")[0]
            old_y = content[i].split("cy=\"")[1].split("\"")[0]
            gene_name = old_pos_dict[str(old_x) + " " + str(old_y)]
            if gene_name in new_pos_dict:
                new_pos = new_pos_dict[gene_name]
                first_half = content[i].split(" cx=")[0]
                second_half = content[i].split("display=")[1]
                content[i] = first_half + " cx=\"" + new_pos[0] + "\" cy=\"" + new_pos[1] + "\" display=" + second_half
                    
        if "<text " in content[i] and "polygon" not in content[i]: #update the text pos #UPDATE 3: polygons don't have info stored in old_pos_dict
            #print(content[i])
            old_text_x = content[i].split("x=\"")[1].split("\"")[0]
            old_text_y = content[i].split("y=\"")[1].split("\"")[0]
            old_x = str(float(old_text_x) - 18)
            old_y = str(float(old_text_y) + 18)
            
            if ".0" in old_x:
                old_x = old_x[:-2]
            if ".0" in old_y:
                old_y = old_y[:-2]
            
            gene_name = old_pos_dict[str(old_x) + " " + str(old_y)]
            if gene_name in new_pos_dict:
                new_pos = new_pos_dict[gene_name]
                new_text_pos = [str(float(new_pos[0]) + 18), str(float(new_pos[1]) - 18)]
                
                first_half = content[i].split("x=")[0]
                second_half = "x=\"" + new_text_pos[0] + "\" y=\"" + new_text_pos[1] + "\">" + gene_name + "</text>\n"
                
                content[i] = first_half + second_half
    
    writeToFile(content, "svg_files/_modified_base.svg")
    
    '''
    
    with open("svg_files/_modified_base.svg") as base:
        new_content = base.readlines()
        
    
    
     #CDOE TO REPLACE THE NODES TO STARS ##UPDATE 2
    #print(REPLACED_STARS)
    for i in range(len(new_content)): #for loop to convert some of the nodes to stars
        if "<g class=\"nwnodecontainer\"" in new_content[i]: #update the text pos
            
            print(new_content[i])
            print(new_content[i+1])
            print(new_content[i+2])
            print(new_content[i+3])
            print(new_content[i+4]) #why aren't these two lines printing?
            print(new_content[i+5])
            
            gene_name = new_content[i+4].split("\">")[1].split("</")[0]
            #print(gene_name)
            #print(gene_name1)
            #gene_name2 = gene_name1
            #print(gene_name2)
            cx = int(new_content[i+1].split("cx=\"")[1].split("\" cy")[0])
            cy = int(new_content[i+1].split("cy=\"")[1].split("\" fill")[0])
            if gene_name in REPLACED_STARS:
                for k in range(5): #note: 	did not change the <g class="nwnodecontainer... " lines because it has no effect on the image shown.
                    new_content[i+k+1] = "" #erase the five lines in the node container tag
                new_content[i+1] = draw_star_text(cx,cy,gene_name)            
         
       #ADDED:
                #if gene_name in FINAL_STARS:
                #    print("do something")
    
    writeToFile(new_content, "svg_files/_modified_base.svg")
    '''
     

    '''
    Purple: FDFT1 and RBP3 (from the top circle)
    Blue: CYP8B1, LRAT, MERTK, RGR, RPE65 (from the top circle)
    Red: CYP51A1, HSD17B7, MSMO1, SC5D, RCVRN (from the second column of the smaller table on the Google Spreadsheet)
    Orange: All the genes from the second column of the larger table on the Google Spreadsheet, that are already not purple, blue, or red
    '''

'''
def draw_star_text(cx, cy, name):# cs and cy are int not strings
    
    string1 = "<polygon points=\"" + str(cx) + "," + str(cy-20) + " " +  str(cx-18) +"," + str(cy+34) + " " +  str(cx+27) + "," +str(cy-2) + " " + str(cx-27) +"," + str(cy-2) + " " + str(cx+18) + "," + str(cy+34) + "\" style=\"fill:blue;stroke-width:5;fill-rule:nonzero;\"/>"
    string2 =  "<text fill=\"white\" filter=\"url(#filter_bg_text)\" stroke=\"white\" stroke-width=\"5\" text-anchor=\"start\" x=\"" + str(cx+10) + "\" y=\"" + str(cy-18) +  "\">" + name + "</text>"
    string3 = "<text fill=\"black\" text-anchor=\"start\" x=\"" + str(cx+10) + "\" y=\"" + str(cy-18) + "\">" + name + "</text>"


    if name in purple:
        string1= string1.replace("blue", "purple")
    elif name in red:
        string1= string1.replace("blue", "red")
    elif name in orange:
        string1= string1.replace("blue", "orange")
        #print(name)
        
    return (string1 + "\n" + string2 + "\n" +string3 + "\n")

#x,y-12 x-18,y+42 x+27,
#y+6 x-27,y+6 x+18,y+42
'''

    
'''

    <polygon points="30,18 12,72 57,36 3,36 48,72 "style="fill:red;stroke-width:5;fill-rule:nonzero;"/>
    <text fill="white" filter="url(#filter_bg_text)" stroke="white" stroke-width="5" text-anchor="start" x="40" y="20">RBP3</text>
    <text fill="black" text-anchor="start" x="40" y="20">RBP3</text>

    <polygon points="30,18 12,72 57,36 3,36 48,72" style="fill:red;stroke-width:5;fill-rule:nonzero;"/>
    <text fill="white" filter="url(#filter_bg_text)" stroke="white" stroke-width="5" text-anchor="start" x="40" y="20">RBP3</text>
    <text fill="black" text-anchor="start" x="40" y="20">RBP3</text>
'''       
            
     

    #the function to distribute the points in a rectangle

def distribute_points(new_pos_dict, a_list, x_left_bound, x_right_bound, y_low_bound, y_up_bound, iso_zone, x_center, y_center):
    new_x_list = []
    new_y_list = []
    key_num = random.SystemRandom()

    for i in range(len(a_list)): 
        a_x_val = -1
        a_y_val = -1
        
        while True: #the statement in the while loop is just for one pick
            count = 0 #number of times we've checked the items ti make sure not overlapping with chosen points

            A_new_x = key_num.randint( x_left_bound, x_right_bound )
            A_new_y = key_num.randint( y_low_bound, y_up_bound )
            
            if iso_zone: 
                dist2 = math.sqrt( abs(x_center -  A_new_x) ** 2 + abs(y_center -  A_new_y) **2  )
                if dist2 < 42:
                    continue

            for j in range(len(new_y_list)):
                dist = math.sqrt(abs(new_x_list[j] -  A_new_x) * abs(new_x_list[j] -  A_new_x) + abs(new_y_list[j] -  A_new_y) * abs(new_y_list[j] -  A_new_y))
                if (dist < 57):
                    break #failed, generate a new number
                count = count + 1
                
            if count == len(new_y_list):
                a_x_val = A_new_x
                a_y_val = A_new_y
                break #when count in 
                
            
        new_x_list.append(a_x_val)
        new_y_list.append(a_y_val)
        new_pos_dict[a_list[i]] = [str(a_x_val), str(a_y_val)] 
        

   
def insert_line(x1, y1, x2, y2, content, i):
    first = "\t\t<g class=\"nwlinkwrapper\" id=\"edge.1111111.1111111\">\n"
    second =	"	\t\t<line class=\"nw_edge\" id=\"line.1111111.1111111.1\" stroke=\"#FF4500\" stroke-dasharray=\"none\" stroke-opacity=\"0.362\" stroke-width=\"7\" style=\"\" x1=\"" + str(x1) + "\" y1=\""+ str(y1)+ "\" x2=\"" + str(x2) + "\" y2=\"" + str(y2)+ "\" />\n"
    
    #index = n
    #second_2 =  "n" + "\" stroke=\"#0000FF\" stroke-dasharray=\"none\" stroke-opacity=\"0.362\" stroke-width=\"5\" style=\"\" x1=\"1609.5\" y1=\"1353.5\" x2=\"489.5\" y2=\"2051.5\" />"
    third = "		</g>\n"
    content.insert(i,third)
    content.insert(i,second)
    content.insert(i,first)
    
    
    

def create_svg(b_gene):

    with open("svg_files/_modified_base.svg") as modified_base:
        content = modified_base.readlines()
    
    naughty_b_list = []
    naughty_d_list = []
    b_list = getListForGroup("B")
    for b in b_list:
        if b != b_gene:
            naughty_b_list.append(b)
            naughty_d_list.append(B_D_PAIR[b])

    naughty_b_numbers = []
    naughty_d_numbers = []

    for i in range(len(content)):
        if "<text fill=\"white\"" in content[i]:
            gene_line = content[i].split("</text>")[0].split(">")[1]
            
            if gene_line in naughty_b_list or gene_line in naughty_d_list:
                naughty_x = content[i-1].split("cx=\"")[1].split("\"")[0]
                naughty_y = content[i-1].split("cy=\"")[1].split("\"")[0]
                
                naughty_x = str(float(naughty_x) + 0.5)
                naughty_y = str(float(naughty_y) + 0.5)
                
                if gene_line in naughty_b_list:
                    naughty_b_numbers.append(naughty_x + " " + naughty_y)
                if gene_line in naughty_d_list:
                    naughty_d_numbers.append(naughty_x + " " + naughty_y)
                    for j in range(i - 4, i + 3):
                        content[j] = ""
    for i in range(len(content)):
        if "<line class" in content[i]:
            x1 = content[i].split("x1=\"")[1].split("\"")[0]
            y1 = content[i].split("y1=\"")[1].split("\"")[0]
            pos1 = x1 + " " + y1
            x2 = content[i].split("x2=\"")[1].split("\"")[0]
            y2 = content[i].split("y2=\"")[1].split("\"")[0]
            pos2 = x2 + " " + y2
            if pos1 in naughty_b_numbers or pos2 in naughty_b_numbers or pos1 in naughty_d_numbers or pos2 in naughty_d_numbers:
                for j in range(i - 1, i + 2):
                    content[j] = ""

    writeToFile(content, "svg_files/" + b_gene + ".svg")


def count_A_group(): #ABCA4, RPE65, RHO 
    a = []
    b = []
    c = []
    ab = []
    bc = []
    ac = []
    abc = []
    loner = []
    
    A_genes = getListForGroup("A")
    print(len(A_genes))
    for gene in A_genes:
        for l in GENE_LIST:
            if gene == l[0]:
                #print(l[0])
                #print(l[1])

                genes_connected = l[1].keys()
                A =  "ABCA4" in genes_connected 
                B = "RPE65" in genes_connected 
                C = "RHO" in genes_connected 
                if gene != "ABCA4" and gene != "RPE65" and gene != "RHO":
                    if (A and B and C):
                        abc.append(gene)
                    elif (A and B and not C):
                        ab.append(gene)
                    elif (A and C and not B):
                        ac.append(gene)
                    elif (B and C and not A):
                        bc.append(gene)
                    elif (A and not B and not C):
                        a.append(gene)
                    elif (B and not A and not C):
                        b.append(gene)
                    elif (C and not A and not B):
                        c.append(gene)
                    else:
                        loner.append(gene)
    
    print("A:" +  str(len(a)))
    print("B:" + str(len(b)))
    print("C:" +  str(len(c)))
    print("AB:" + str(len(ab)))
    print("BC:" + str(len(bc)))
    print("AC:" + str(len(ac)))
    print("ABC:" + str(len(abc)))
    print("loner:" + str(len(loner)))
    
    print(len(a) + len(b) +len(c) + len(ab) + len(bc) + len(ac) + len(abc) + len(loner) )
    l = []
    l.append(a)
    l.append(b)
    l.append(c)
    l.append(ab)
    l.append(bc)
    l.append(ac)
    l.append(abc)
    
    half = len(loner)/2
    loners_left = loner[:half]
    loners_right = loner[half:]

    l.append(loners_left)
    l.append(loners_right)
    return l 
                    
    #print(GENE_LIST) # a list of lists (that contains the gene name and the dictionary)


#list of gene names
    
    



def dict_max(dic): #given a dictionary of string to int pairs, return the string that yielded the max value
    maximum = max(dic.values())
    inv_map = {v: k for k, v in dic.items()}
    return inv_map[maximum]
    
def print_dic(dic):
    for key,value in dic.items():
        print(key)
        print(len(value))
        print(value)
        
    #
#def 
    #given a list


#GENE_LIST_UNGROUPED is just a list of genes
#GENE_LIST_PARENT is a list og lists, where the inner list is the gene name and a dic that maps to children and conf level
#GENE_TREE is the dic that maps parent to children
def subtree_once(GENE_LIST_PARENT, GENE_LIST_UNGROUPED, GENE_TREE):
    
    NEW_PARENTS = []
    NEW_UNGROUPED = []
    
    
    for gene in GENE_LIST_UNGROUPED:
        dic = {} #each ungrouped gene gets its down dic. dic has "gene_parent string" to confidence interval data 
        for i in range(len(GENE_LIST_PARENT)): #run for all the parents
            gene_parent = GENE_LIST_PARENT[i][0]
            gene_dic = GENE_LIST_PARENT[i][1]
            if gene in gene_dic.keys():
                dic[gene_parent] = gene_dic[gene] 
                
        if len(dic) != 0:#found a matching parent
            winner = dict_max(dic)
            GENE_TREE[winner].append(gene)
            
            NEW_PARENTS.append(gene)
        else:
            NEW_UNGROUPED.append(gene)
            '''
            if winner == "ABCA4":
                GROUP_ABCA4.append(gene)
            elif winner == "RPE65":
                GROUP_RPE65.append(gene)
            elif winner == "RHO":
                GROUP_RHO.append(gene)
            '''
    #print("detected %s circle(s)" %count)
    
    #Update these two for the next iteration:
    #GENE_LIST_UNGROUPED = [gene for gene in GENE_LIST_UNGROUPED if gene not in NEW_PARENTS ]
    
    #print_dic(GENE_TREE)
    
    GENE_LIST_PARENT[:] = [l for l in GENE_LIST if l[0] in  NEW_PARENTS]
    GENE_LIST_UNGROUPED[:] = NEW_UNGROUPED
    
    #NEW_PARENTS_list_dic = [l for l in GENE_LIST if l[0] in  NEW_PARENTS]
    
    #return (NEW_PARENTS_list_dic, NEW_UNGROUPED)
    
    #Ran one level
    
 
    
    #return GENE_LIST_UNGROUPED
    

    #print(len(GENE_LIST_removed))




    

#two purposes: 
#returns a dict that maps parent nodes to its children nodes
#Modify the LAYERS variable so that it is a list of the genes in level1 ,leve2, ..
def create_tree_dict(GENE_LIST_PARENT, GENE_LIST_UNGROUPED, LAYERS):
    
    #global LAYERS
    GENE_TREE = defaultdict(list)
    layer_count =[]
    genes_this_layer = [l[0] for l in GENE_LIST_PARENT]
    LAYERS.append(genes_this_layer)
    layer_count.append(len(GENE_LIST_PARENT))
   
    while GENE_LIST_UNGROUPED!= []:
        count = len(GENE_LIST_UNGROUPED)
        subtree_once(GENE_LIST_PARENT, GENE_LIST_UNGROUPED, GENE_TREE)
        
        
        genes_this_layer = [l[0] for l in GENE_LIST_PARENT] #list of list of (gene name , dictionary)
      
        
        LAYERS.append(genes_this_layer)
        layer_count.append(len(GENE_LIST_PARENT))
        if count == len(GENE_LIST_UNGROUPED): #if a subtree_once call the count hasn't change, we know we can't group anymore and we break
            break
    
    print("UNGROUPED:")
    print(GENE_LIST_UNGROUPED)
    print("Layer count")
    print(layer_count)
    
    return GENE_TREE




#wreturns the svg code for a circle
def create_circle_code(x, y, r, name): 


    dx = 3500 - x
    dy = 3500 - y
    angle = math.pi/2 #for dy = 0
    if dy!= 0:
        angle = math.atan(dx/dy)
 
    
    radius = math.sqrt(dx**2 + dy**2)
    new_radius = radius + 130
  

    new_dx = abs(new_radius * math.sin(angle))
    new_dy = abs(new_radius * math.cos(angle))
    
    
    text_x = 3500
    text_y = 3500
    if dx > 0:
        text_x -= new_dx #right now the center circle is at 3500,3500 #can do text_x =  x + 45 too
    else:
        text_x += new_dx #right now the center circle is at 3500,3500 #can do text_x =  x + 45 too
    
    if dy > 0:
        text_y -= new_dy
    else:
        text_y += new_dy
        


    '''
    line1 = ""
    line2 = ""
    line3 = ""
    line4 = "" 
    line5 = ""
    line6 = ""
    '''
      
    line1 = "<g class=\"nwnodecontainer\" data-action_option=\"_unassigned\" data-exp_height=\"250\" data-exp_width=\"324\" data-payload_text=\"\" data-radius=\""  + str(r) + "\" data-safe_div_label=\"" + name + "\" data-x_pos=\"662\" data-y_pos=\"50\" id=\"node.4433068\">"+"\n"
    line2 = "<circle cx=\"" + str(x) +"\" cy=\"" + str(y) + "\" fill=\"url(#bubble_gradient1)\" r=\"" + str(r) +"\" />" +"\n"
    line3 =	"<circle cx=\"" +str(x) + "\" cy=\"" +str(y)+ "\" fill=\"url(#bubble_gradient2)\" opacity=\"0.33\" r=\"" + str(r) +"\" />" +"\n"
    line4 =	"<circle class=\"nwbubblecoloredcircle\" cx=\"" +str(x) + "\" cy=\"" +str(y) + "\" display=\"initial\" fill=\"rgb(52,152,219)\" r=\"" +str(r) + "\" />" + "\n"
    line5 = "<text font-family=\"Arial\" font-size=\"40px\" fill=\"white\" filter=\"url(#filter_bg_text)\" stroke=\"white\" stroke-width=\"5\" text-anchor=\"middle\" x=\"" +str(text_x) + "\" y=\"" +str(text_y) + "\">" +str(name) + "</text>" +"\n"
    line6 =	"<text font-size=\"40px\" fill=\"black\" text-anchor=\"middle\" x=\"" +str(text_x) + "\" y=\"" +str(text_y) + "\">" +str(name) + "</text>" + "\n" + "</g>" + "\n"
    #print("<g class=\"nwnodecontainer\" data-action_option=\"_unassigned\" data-exp_height=\"250\" data-exp_width=\"324\" data-payload_text=\"\" data-radius=\"")
    return line1+line2+line3+line4+line5+line6


    
def create_tree_svg_helper(LAYERS,  width, height):
    content = []
    content.append("<svg class=\"notselectable\" height=\"" +str(height)+ "\" id=\"svg_network_image\" width=\"" + str(width) +"\" xmlns=\"http://www.w3.org/2000/svg\" xmlns:svg=\"http://www.w3.org/2000/svg\" xmlns:xlink=\"http://www.w3.org/1999/xlink\">")


    #
    #with open("svg_files/tree.svg") as tree: #5000 * 4000
    #    content = tree.readlines()
    x = 0 
    y = 0
    r = 40
  
    
    y_unit = round(height/ (len(LAYERS) +2))
    for i in range(len(LAYERS)):
        layer_length = len(LAYERS[i])
        x_unit = round(width/(layer_length +4))
        for k in range(layer_length):
            x_pos = x+(k+1)*x_unit
            y_pos = y +(i+1) * y_unit
            name = LAYERS[i][k] 
            code =  create_circle_code(x_pos, y_pos, r, name)
            content.append(code)
        
    content.append("</svg>")
    
    writeToFile(content, "svg_files/tree.svg")
    
   
outmost_gene_count = 0
outmost_radius = 0
def store_circ_tree_pos(circ_tree_pos_dict, gene_list, center_x, center_y, PARENT_TO_CHILD, standout):
    global outmost_gene_count
    global outmost_radius

    gene_num = len(gene_list)
    radius = 0
    #print("radius")
    #print(radius)
    if outmost_radius == 0:
        radius = gene_num * 28
    else: #
        #check if the neighboring cicles are too close. If the num of genes are less than 10 percent about, then manually times 1.15 to the outer radius
        percent_increase = 0
        if outmost_gene_count!=0:
            percent_increase = (gene_num - outmost_gene_count)/outmost_gene_count 
            if percent_increase > 0:
                radius = int(round(outmost_radius* (1.3 + percent_increase )) ) #1.3
            elif percent_increase < 0:
                radius = outmost_radius * 1.2 #1.2

    outmost_radius = radius
    outmost_gene_count = gene_num #update outmost_gene_count
    
    #print("radius")
    #print(radius)
    #figure out the proper range: i from 0-7
    for i in range(gene_num): 
        x = int(round(center_x  + radius * math.cos(6.28/len(gene_list)*i) ))
        y = int(round(center_y + radius * math.sin(6.28/len(gene_list)*i) ))
        circ_tree_pos_dict[gene_list[i]] = [ x, y ]
        
        if standout == True and len(PARENT_TO_CHILD[gene_list[i]]) > 4:
            circ_tree_pos_dict[gene_list[i]] = [ x+0.1*radius*math.cos(6.28/len(gene_list)*i), y+0.1*radius*math.sin(6.28/len(gene_list)*i)]
        '''
        else: #if they're a star, need special code to generate the stars
            star_code = draw_star_text(x,y, gene_list[i]) #UPDATE 1: Insert star_cpde when making the cirlce
            length = len(content)
            content.insert(length-1, star_code)
        '''

#calculate the position of the genes in a circle and store it into circ_tree_pos_dict
#1.12, 1.2 and 1.07 are arbitrary and maybe needs to be passed in
    
def store_circ_tree_pos2(LAYERS,circ_tree_pos_dict, width, height):
    outmost_radius = 0
    outmost_gene_count = 0
    for layer in LAYERS:
            outmost_radius, outmost_gene_count = store_circ_tree_pos_helper(circ_tree_pos_dict,layer, width/2, height/2, outmost_radius, outmost_gene_count) 
        

def store_circ_tree_pos_helper(circ_tree_pos_dict, gene_list, center_x, center_y,outmost_radius, outmost_gene_count):
    #global outmost_gene_count
    #global outmost_radius

    gene_num = len(gene_list)
    radius = 0
    #print("radius")
    #print(radius)
    if outmost_radius == 0:
        radius = gene_num * 25
    else: #
        #check if the neighboring cicles are too close. If the num of genes are less than 10 percent about, then manually times 1.15 to the outer radius
        percent_increase = 0
        if outmost_gene_count!=0:
            percent_increase = (gene_num - outmost_gene_count)/outmost_gene_count 
            if percent_increase > 0:
                radius = int(round(outmost_radius* (1.3 + percent_increase )) )
            elif percent_increase < 0:
                radius = outmost_radius * 1.2

    outmost_radius = radius
    outmost_gene_count = gene_num #update outmost_gene_count
    
    #print("radius")
    #print(radius)
    #figure out the proper range: i from 0-7
    for i in range(gene_num): 
        x = int(round(center_x  + radius * math.cos(6.28/len(gene_list)*i) ))
        y = int(round(center_y + radius * math.sin(6.28/len(gene_list)*i) ))
        circ_tree_pos_dict[gene_list[i]] = [ x, y ]
    return (outmost_radius,outmost_gene_count)
   

#flow:
 #   1. store the node location in the global variable circ_tree_pos_dict by caling store_circ_tree_pos
  #  2. geeneate the svg code based on the location, then create an svg and write code to it
    


def create_edge_code(x1,y1,x2,y2):
    '''
    <g class="nwlinkwrapper" id="edge.4440022.4432753">
    			<line class="nw_edge" id="line.4440022.4432753.1" stroke="#1F294A" stroke-dasharray="none" stroke-opacity="0.181" stroke-width="1.086" style="" x1="1131.5" y1="4403.5" x2="2673.5" y2="2583.5" />
    		</g>
    '''
    line1 =  "<g class=\"nwlinkwrapper\" id=\"edge.4440022.4432753\">\n"
    line2 =  "<line class=\"nw_edge\" id=\"line.4440022.4432753.1\" stroke=\"#1F294A\" stroke-dasharray=\"none\" stroke-opacity=\"0.7\" stroke-width=\"1.286\" style=\"\" x1=\"{x1}\" y1=\"{y1}\" x2=\"{x2}\" y2=\"{y2}\" />\n".format(x1 = x1, y1=y1, x2=x2, y2=y2)
    line3 =  "</g>\n"
    return line1+line2+line3
 



#actually writes the svg code to file
def create_circ_tree_svg_helper(LAYERS, circ_tree_pos_dict, width, height, PARENT_TO_CHILD, file_name):        
    content = []
    content.append("<svg class=\"notselectable\" height=\"" +str(height)+ "\" id=\"svg_network_image\" width=\"" + str(width) +"\" xmlns=\"http://www.w3.org/2000/svg\" xmlns:svg=\"http://www.w3.org/2000/svg\" xmlns:xlink=\"http://www.w3.org/1999/xlink\">")


    #
    #with open("svg_files/tree.svg") as tree: #5000 * 4000
    #    content = tree.readlines()
    #x = 0 
    #y = 0'=
    
    #try ordering layer by number of children. two steps: convert the layer list into a list of dic
    #then sort the dictionary
    #then convert the dic back to a list
    
    LAYERS_SORTED = []
    
    for genes_this_layer in LAYERS:
        #gene to number of children mapping
        genes_this_layer_dic = { gene: len(PARENT_TO_CHILD[gene]) for gene in genes_this_layer  }
        genes_sorted = [gene for gene, num_children in sorted(genes_this_layer_dic.items(), key=lambda item: item[1], reverse=True )]
        #print(genes_sorted)
        #print(genes_this_layer_dic)
        LAYERS_SORTED.append(genes_sorted)
    
    #print(LAYERS_SORTED)
    #print(LAYERS)
    LAYERS_ALIGNED = [] #each layer of gene is ordered by parent gene1's children, then parent gene 2's children,...
    LAYERS_ALIGNED.append(LAYERS[0])
    for i in range(len(LAYERS_SORTED)):
        gene_parents = LAYERS_ALIGNED[i]
        children_ordered = [] 
        for gene_parent in gene_parents:
            children = PARENT_TO_CHILD[gene_parent]
            #print("children count:{}".format(len(children)))
            
            #reorder children_to_add so that the top 3 elements that have more than 5 gene connections are spaced out
            children_to_add = [child for child in children if child not in children_ordered ]
            
            children_10 =  [child for child in children_to_add if len(PARENT_TO_CHILD[child]) > 10 ] 
            dic_10 = { gene: len(PARENT_TO_CHILD[gene]) for gene in children_10  }
            children_10_sorted = [gene for gene, num_children in sorted(dic_10.items(), key=lambda item: item[1], reverse=False )]
            #print(children_10_sorted)
            #rint(children_10)
            
            children_3_9 = [child for child in children_to_add if len(PARENT_TO_CHILD[child]) > 2 and len(PARENT_TO_CHILD[child]) < 10]
            dic_3_9 = { gene: len(PARENT_TO_CHILD[gene]) for gene in children_3_9  }
            children_3_9_sorted = [gene for gene, num_children in sorted(dic_3_9.items(), key=lambda item: item[1], reverse=False )]
            #print(children_3_9_sorted)
            #print(children_3_9)
            
            children_0_2 = [child for child in children_to_add if child not in children_3_9 and child not in children_10 ]
            dic_0_2 = { gene: len(PARENT_TO_CHILD[gene]) for gene in children_0_2  }
            children_0_2_sorted = [gene for gene, num_children in sorted(dic_0_2.items(), key=lambda item: item[1], reverse=False )]
            #print(children_0_4_sorted)
            
            #circ tree 2 : reverse= false, 20, 7
            #circ tree 2 : reverse= false, 10, 20
            
            #circ tree 1: reverse = false
        
            children_to_add_reorderd = []
            for child in children_10_sorted:
                children_to_add_reorderd.append(child)
                children_to_add_reorderd.extend(children_0_2_sorted[:10])
                children_0_2_sorted[:] = children_0_2_sorted[10:]
            
            for child in children_3_9_sorted:
                children_to_add_reorderd.append(child)
                children_to_add_reorderd.extend(children_0_2_sorted[:5])
                children_0_2_sorted[:] = children_0_2_sorted[5:]
            
            children_to_add_reorderd.extend(children_0_2_sorted)
            children_ordered.extend(children_to_add_reorderd)

            #children_ordered.extend(children_to_add)
       
        if children_ordered != []: 
            LAYERS_ALIGNED.append(children_ordered)
        else: #reacheed the end of the tree
            break
    print(LAYERS_ALIGNED)
        
    
    #store_circ_tree_pos(LAYERS_ALIGNED, circ_tree_pos_dict,width, height)
    
    for layer in LAYERS_ALIGNED:
        store_circ_tree_pos(circ_tree_pos_dict,layer, width/2, height/2, PARENT_TO_CHILD, True ) 
    
    
    global outmost_radius 
    global outmost_gene_count
    outmost_radius =  0 #reset the global params
    outmost_gene_count =  0
    

    #APPENDING NODE SVG CODE
    r = 16 #radius of the node itself, not the cirle of nodes
    for i in range(len(LAYERS_ALIGNED)):
        layer_length = len(LAYERS_ALIGNED[i])
        for k in range(layer_length):
            name = LAYERS_ALIGNED[i][k]
            x_pos = circ_tree_pos_dict[name][0]
            y_pos = circ_tree_pos_dict[name][1]
            code =  create_circle_code(x_pos, y_pos, r, name)
            content.append(code)
        
    content.append("\n")
    
    
    #APPENDING EDGE SVG CODE
    
    for parent, children in PARENT_TO_CHILD.items():
        x1 = circ_tree_pos_dict[parent][0]
        y1 = circ_tree_pos_dict[parent][1]
        for child in children:
            x2 = circ_tree_pos_dict[child][0]
            y2 = circ_tree_pos_dict[child][1]
            edge_code = create_edge_code(x1,y1,x2,y2)
            content.append(edge_code)
    
    
    #edge_code = create_edge_code(100,100,200,200)
    #content.append(edge_code)

    content.append("</svg>")
    
    writeToFile(content, "svg_files/{file_name}".format(file_name = file_name) )
    
 
 
def create_circle_svg(parent, exclude, file_name):
    LAYERS = []

    GENE_LIST_PARENT = [l for l in GENE_LIST if l[0] in parent ] #list of list of (gene name , dictionary)
    GENE_LIST_UNGROUPED = [l[0] for l in GENE_LIST if l[0] not in  exclude ]
    
    PARENT_TO_CHILD = create_tree_dict(GENE_LIST_PARENT, GENE_LIST_UNGROUPED, LAYERS)
    #print("LAYERS:\n")
    #print(LAYERS)
    
    #print("Parent to child mapping:")
    #print(PARENT_TO_CHILD)
    
    #tree_height = 4000
    #tree_width = 8000
    #create_tree_svg_helper(LAYERS, tree_width, tree_height)
    
    
    circ_tree_pos_dict1 = defaultdict(list) #maps gene name to position
    
    circ_tree_height = 7000
    circ_tree_width = 7000
    create_circ_tree_svg_helper(LAYERS, circ_tree_pos_dict1, circ_tree_width, circ_tree_height, PARENT_TO_CHILD, file_name)
    
    
    

    
    
     
def main():   
    #os.system('mkdir info_files')
    #os.system('mkdir svg_files')
    os.system('touch ' + GENE_DATABASE_FILE)
    os.system('touch ' + UNIDENTIFIABLE_GENE_FILE)
    os.system('touch ' + CHANGED_NAME_GENE_FILE)
    readDatabase()
    readUnidentifiable()
    readChangedName()
    
    
    parseInput()
    #groups_expanded = classify(groups) 

    writeGeneGroups()
    writeUnidentifiable()
    writeChangedName()

    
    '''
    entire_list = []
    entire_list.extend(getListForGroup("A"))
    entire_list.extend(getListForGroup("B"))
    entire_list.extend(getListForGroup("C"))
    entire_list.extend(getListForGroup("D"))
    '''
    
    parent_1 = ["ABCA4", "RHO"]
    exclude1 = ["ABCA4", "RPE65", "RHO"]
    file_name = "circle_tree_1.svg"
    create_circle_svg(parent_1, exclude1,file_name )
    
    
    parent_2 = ["RPE65"]
    file_name = "circle_tree_2.svg"
    create_circle_svg(parent_2, parent_2, file_name)
    
    
    parent_3 = ["ABCA4"]
    file_name = "circle_tree_3.svg"
    create_circle_svg(parent_3, parent_3,file_name )
    
    parent_4 = ["RHO"]
    file_name = "circle_tree_4.svg"
    create_circle_svg(parent_4, parent_4,file_name )

    
    #print_dic(GENE_TREE_1)
    
    
    
    #GENE_TREE_2 = defaultdict(list)
    '''
    LAYERS2 = []
    GENE_LIST_PARENT = [l for l in GENE_LIST if l[0] in  {"RPE65"} ] #list of list of (gene name , dictionary)
    GENE_LIST_UNGROUPED = [l[0] for l in GENE_LIST if l[0] not in  {"RPE65"} ]
    
    GENE_TREE_2 = create_tree_dict(GENE_LIST_PARENT, GENE_LIST_UNGROUPED,LAYERS2)
    print("LAYERS:\n")
    print(LAYERS2)
    print(GENE_TREE_2)
    '''
    #print_dic(GENE_TREE_2)
    
    #print(draw_gene(1728, 3391, 20, "ARL2BP"))


    
    
    
    '''
    #print(GENE_LIST_UNGROUPED)
    
    layer_count =[]
    layer_count.append(len(GENE_LIST_PARENT))
   
    while GENE_LIST_UNGROUPED!= []:
        count = len(GENE_LIST_UNGROUPED)
        subtree_once(GENE_LIST_PARENT, GENE_LIST_UNGROUPED, GENE_TREE_1)
        layer_count.append(len(GENE_LIST_PARENT))
        if count == len(GENE_LIST_UNGROUPED):
            break
    
    print(GENE_TREE_1)
    print_dic(GENE_TREE_1)
    print(GENE_LIST_UNGROUPED)
    print(layer_count)
    '''
    
    

    #while GENE_LIST_UNGROUPED!= []:
     #   subtree_once()
    
    #print_dic(GENE_TREE)
    
    #print("entire_list")
    #print(entire_list)
    '''
        
    for gene in group1:
        if gene not in entire_list :
            entire_list.append(gene)
    
    for gene in group2:
        if gene not in entire_list :
            entire_list.append(gene)
            
    for gene in group3:
        if gene not in entire_list :
            entire_list.append(gene)
            
            
    for gene in group4:
        if gene not in entire_list :
            entire_list.append(gene)
    
    
    #download_svg(entire_list)
    
    
    
    #print(draw_star_text(30,30, "RBP3"))
    
    #print("group 1:")
    #print(groups_expanded[0])
    
    #modify_base_svg(groups_expanded)
    
    
    
    b_list = getListForGroup("B")
    for b_gene in b_list:
        create_svg(b_gene)
    
    
    '''
    
if __name__ == "__main__":
    main()
'''
defaultdict(<class 'list'>, {'RHO': ['AKAP9', 'AKT1', 'ALB', 'ARL3', 'BBS1', 'BBS2', 'CNGA1', 'CNGB1', 'CRX', 'GAPDH', 'GUCA1B', 'INS', 'NEUROD1', 'NR2E3', 'NRL', 'PDE6A', 'PDE6B', 'PDE6G', 'PRPF31', 'PRPF8', 'PRPH2', 'RBP3', 'RCVRN', 'RGR', 'ROM1', 'RP1', 'RP9', 'SAG', 'STAT3'], 'RPE65': ['BEST1', 'CRB1', 'FDFT1', 'IDH3B', 'IMPDH1', 'KLHL7', 'LRAT', 'MERTK', 'PRCD', 'RDH12', 'RLBP1', 'SNRNP200', 'SPATA7', 'TOPORS', 'TULP1'], 'ABCA4': ['C2orf71', 'C8orf37', 'CERKL', 'CLRN1', 'EYS', 'FAM161A', 'FSCN2', 'IMPG2', 'PROM1', 'PRPF3', 'RP1L1', 'RPGR', 'SEMA4A', 'USH2A', 'ZNF513'], 'FDFT1': ['ACAT1', 'CH25H', 'CYP51A1', 'CYP8B1', 'DHCR7', 'DHDDS', 'FAXDC2', 'HSD17B7', 'LSS', 'MSMO1', 'MVK', 'PPARA', 'SC5D', 'SP1', 'SQLE', 'TM7SF2'], 'IMPDH1': ['ACLY', 'CAD'], 'INS': ['ADIPOR1', 'HK1', 'PPARG', 'SLC2A4'], 'STAT3': ['AHR', 'GHR', 'IL6', 'KDM6B', 'MAF'], 'RPGR': ['ARAP2'], 'ARL3': ['ARL2BP', 'KPNA2', 'RP2'], 'BBS1': ['ARL6', 'IFT140', 'IFT172'], 'AKT1': ['ARNT', 'DECR1', 'HSP90AA1', 'MYC', 'NOS3'], 'RP9': ['CA4'], 'AKAP9': ['CEP70', 'KIAA1549', 'NEK2', 'OFD1', 'PRKAR2B'], 'SNRNP200': ['DHX38', 'PRPF4', 'PRPF6'], 'CNGB1': ['DTHD1'], 'GAPDH': ['ENO1', 'ENO2', 'ENO3', 'ENO4', 'PARK2', 'UBC'], 'PROM1': ['GPR125'], 'IDH3B': ['IDH2'], 'RP1L1': ['MAK'], 'ALB': ['PRDM10', 'SPP2'], 'PRPF8': ['RANBP2', 'XPO1'], 'NR2E3': ['SAMD11'], 'TOPORS': ['SIN3A'], 'C2orf71': ['ZNF408'], 'ADIPOR1': ['CDH13'], 'LSS': ['CYP4V2'], 'DTHD1': ['EMC1'], 'UBC': ['FBXL19', 'UBXN1'], 'HK1': ['GNPDA1'], 'KDM6B': ['KDM2A', 'KDM2B'], 'IDH2': ['KDM6A'], 'XPO1': ['KPNA7', 'XRN1'], 'ENO1': ['PYGL'], 'KIAA1549': ['SRGAP2', 'SRGAP3'], 'OFD1': ['TCOF1'], 'SP1': ['TSPO'], 'CYP4V2': ['ABCB6'], 'TCOF1': ['HCCS']})
RHO
29
['AKAP9', 'AKT1', 'ALB', 'ARL3', 'BBS1', 'BBS2', 'CNGA1', 'CNGB1', 'CRX', 'GAPDH', 'GUCA1B', 'INS', 'NEUROD1', 'NR2E3', 'NRL', 'PDE6A', 'PDE6B', 'PDE6G', 'PRPF31', 'PRPF8', 'PRPH2', 'RBP3', 'RCVRN', 'RGR', 'ROM1', 'RP1', 'RP9', 'SAG', 'STAT3']

RPE65
15
['BEST1', 'CRB1', 'FDFT1', 'IDH3B', 'IMPDH1', 'KLHL7', 'LRAT', 'MERTK', 'PRCD', 'RDH12', 'RLBP1', 'SNRNP200', 'SPATA7', 'TOPORS', 'TULP1']

ABCA4
15
['C2orf71', 'C8orf37', 'CERKL', 'CLRN1', 'EYS', 'FAM161A', 'FSCN2', 'IMPG2', 'PROM1', 'PRPF3', 'RP1L1', 'RPGR', 'SEMA4A', 'USH2A', 'ZNF513']


FDFT1
16
['ACAT1', 'CH25H', 'CYP51A1', 'CYP8B1', 'DHCR7', 'DHDDS', 'FAXDC2', 'HSD17B7', 'LSS', 'MSMO1', 'MVK', 'PPARA', 'SC5D', 'SP1', 'SQLE', 'TM7SF2']

IMPDH1
2
['ACLY', 'CAD']

INS
4
['ADIPOR1', 'HK1', 'PPARG', 'SLC2A4']


STAT3
5
['AHR', 'GHR', 'IL6', 'KDM6B', 'MAF']


RPGR
1
['ARAP2']


ARL3
3
['ARL2BP', 'KPNA2', 'RP2']

BBS1
3
['ARL6', 'IFT140', 'IFT172']
AKT1
5
['ARNT', 'DECR1', 'HSP90AA1', 'MYC', 'NOS3']
RP9
1
['CA4']
AKAP9
5
['CEP70', 'KIAA1549', 'NEK2', 'OFD1', 'PRKAR2B']
SNRNP200
3
['DHX38', 'PRPF4', 'PRPF6']
CNGB1
1
['DTHD1']
GAPDH
6
['ENO1', 'ENO2', 'ENO3', 'ENO4', 'PARK2', 'UBC']
PROM1
1
['GPR125']
IDH3B
1
['IDH2']
RP1L1
1
['MAK']
ALB
2
['PRDM10', 'SPP2']
PRPF8
2
['RANBP2', 'XPO1']
NR2E3
1
['SAMD11']
TOPORS
1
['SIN3A']
C2orf71
1
['ZNF408']
ADIPOR1
1
['CDH13']
LSS
1
['CYP4V2']
DTHD1
1
['EMC1']
UBC
2
['FBXL19', 'UBXN1']
HK1
1
['GNPDA1']
KDM6B
2
['KDM2A', 'KDM2B']
IDH2
1
['KDM6A']
XPO1
2
['KPNA7', 'XRN1']
ENO1
1
['PYGL']
KIAA1549
2
['SRGAP2', 'SRGAP3']
OFD1
1
['TCOF1']
SP1
1
['TSPO']
CYP4V2
1
['ABCB6']
TCOF1
1
['HCCS']
['AGBL5', 'ARHGAP22', 'ARHGAP24', 'ARHGEF18', 'CAPN13', 'CDON', 'GNA13', 'HGSNAT', 'KIZ', 'POMGNT1', 'PTPN23', 'REEP6', 'SLC7A14', 'TRNT1']

'''
