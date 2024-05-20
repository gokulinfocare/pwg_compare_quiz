# This program uses XML data and use streamlit to update the data and then generate a new XML file
# Have to change the path mentioned for saving updated XML file
import streamlit as st 
import xml.etree.ElementTree as ET
import sys
import pandas as pd
import base64
import os
import pdb
from function_moodle_xml_create import create_moodle_xml

# Function to get data from XML file
def get_data_from_xml():

    xml_table = []              # List to store the data from XML file
    new_filename = "updated.xml"   # Default name for updated XML file
    
    st.set_page_config(page_title="Please upload XML file to display/edit the data", layout="wide")
    
    file_name = st.file_uploader("Choose the XML file you want to display/edit")
    if file_name is not None:
        cgpt_table = []
        gem_table = []
        new_filename = file_name.name[:-4] + "updated.xml"
        file_contents = file_name.read().decode("utf-8")
        root = ET.fromstring(file_contents)
        xml_table = []
        #Takes data from the XML file uploaded and stores it in a list of dictionaries
        for element in root.findall('.//question'):
            if element.attrib['type'] == 'multichoice':
                moodle_id = qtext = soln = option1 = option2 = option3 = option4 = answer = ''     
                moodle_id = element.find('.//name/text').text
                qtext = element.find('.//questiontext/text').text
                soln = element.find('.//correctfeedback/text').text
                w_count = 1
                w_incorrect_feedback = ""
                xml_feedback = ""
                for rec in element.findall('.//answer'):
                    if w_incorrect_feedback == "":
                        if rec.find('feedback/text') is not None:
                            xml_feedback = rec.find('feedback/text').text
                        if xml_feedback is not None:
                            w_incorrect_feedback = xml_feedback
                    if w_count == 1:
                        option1 = rec.find('text').text
                        if rec.attrib['fraction'] == '100':
                            answer = 'A'
                    elif w_count == 2:
                        option2 = rec.find('text').text
                        if rec.attrib['fraction'] == '100':
                            answer = 'B'
                    elif w_count == 3:
                        option3 = rec.find('text').text
                        if rec.attrib['fraction'] == '100':
                            answer = 'C'
                    elif w_count == 4:
                        option4 = rec.find('text').text
                        if rec.attrib['fraction'] == '100':
                            answer = 'D'
                    w_count += 1
                struc = {
                    'moodle_id': moodle_id[2:],
                    'questiontext': qtext,                    
                    'option1': option1,
                    'option2': option2,
                    'option3': option3,
                    'option4': option4,
                    'answer': answer,
                    'soln': soln,
                    'incorrect_feedback': w_incorrect_feedback
                }
                if moodle_id[:2] == 'C_':
                    cgpt_table.append(struc)
                elif moodle_id[:2] == 'G_':
                    gem_table.append(struc)
                #xml_table.append(struc)
        # Get the filename from the file_uploader widget
        filename = file_name.name
        
        # Get the file extension
        file_extension = filename.split(".")[-1]
        
        # Create the new filename with "_updated.xml" suffix
        new_filename = filename.replace(f".{file_extension}", "_updated.xml")
        
        # # Check if the number of records is 50
        # if len(xml_table) != 50:
        #     print("50 records not found in XML file")
        #     sys.exit()

    # Prepare in comparison mode
        for gpt in cgpt_table:
            for gem in gem_table:
                if gem['moodle_id'] == gpt['moodle_id']:
                    #w_gpt_text = 'ChatGPT Verison 4o Moodle Id: ' + gpt['moodle_id']
                    #w_gem_text = 'Gemini Latest Version Moodle Id: ' + gem['moodle_id']
                    w_gpt_text = ""
                    w_gem_text = ""
                    w_gpt_text = w_gpt_text + '\n\n' + 'Question Text:' + gem['questiontext'] + '\n\n' + 'Option A: ' + gem['option1'] + '\n\n' + 'Option B: ' + gem['option2'] + '\n\n' + 'Option C: ' + gem['option3'] + '\n\n' + 'Option D: ' + gem['option4'] + '\n\n' + 'Correct Answer: ' + gem['answer'] + '\n\n' + 'Solution: ' + gem['soln'] 
                    w_gem_text = w_gem_text + '\n\n' + 'Question Text:' + gpt['questiontext'] + '\n\n' + 'Option A: ' + gpt['option1'] + '\n\n' + 'Option B: ' + gpt['option2'] + '\n\n' + 'Option C: ' + gpt['option3'] + '\n\n' + 'Option D: ' + gpt['option4'] + '\n\n' + 'Correct Answer: ' + gpt['answer'] + '\n\n' + 'Solution: ' + gpt['soln'] 
                    w_gem_text = w_gem_text.replace('<br>', '\n')
                    w_gpt_text = w_gpt_text.replace('<br>', '\n')
                    # cgpt_len = len(w_gpt_text)
                    # gem_len = len(w_gem_text)
                    # if cgpt_len > gem_len:
                    #     w_diff = cgpt_len - gem_len
                    #     st.write(w_diff)
                    #     w_blank = 'hi'
                    #     w_blank = w_blank + (' ' * w_diff ) 
                    #     w_blank = w_blank + 'end'
                    #     st.write(w_blank)                                              
                    #     w_gem_text = w_gem_text + w_blank                                             
                    # elif gem_len > cgpt_len:                        
                    #     w_diff = gem_len - cgpt_len
                    #     w_blank = (' ' * w_diff)  + 'hi'
                    #     w_gpt_text = w_gpt_text + w_blank    
                    struc = {
                        'cgpt': w_gpt_text,
                        'gem': w_gem_text
                    }
                    
                    xml_table.append(struc)
    
    return xml_table , new_filename         # Return the data and new filename

# Function to display original data 
def display_data(data):
    # st.write("### Original Data:")
    # st.dataframe(data) 
    col1, col2 = st.columns([1, 1])   
    for rec in data:
        #pdb.set_trace()        
        with col1:
            st.write("### ChatGPT Version")
            st.write(rec['cgpt'])
            #st.text_area(rec['cgpt'])
        with col2:
            st.write("### Gemini Version")
            st.write(rec['gem'])
            #st.text_area(rec['gem'])
        


# Function to edit data
def edit_data(data):
    st.write("### Edit Data:")
    num_rows = len(data)

    # Get column names from the keys of the first dictionary in the list
    if num_rows > 0:
        column_names = list(data[0].keys())
    else:
        column_names = []

    # Create empty DataFrame with columns
    edited_data = pd.DataFrame(columns=column_names, index=range(num_rows))
    data = pd.DataFrame(data)           #Convert the list of original data to a dataframe
    for i in range(len(data)):
        for col in data.columns:
            if len(data.at[i, col]) > 180:     #If the length of the data is more than 180 chars
                edited_data.at[i, col] = st.text_area(f"Row {i+1} - {col}", data.at[i, col],  height=125)
            else:
                edited_data.at[i, col] = st.text_input(f"Row {i+1} - {col}", data.at[i, col])   #Edits the data in the dataframe
    return edited_data


def create_xml(data,new_filename):
    
    xml_modified_data = create_moodle_xml(data)
    xml_data_utf8 = xml_modified_data.encode('utf-8')
    st.download_button(
        label="Save Changes and Download XML File",
        data=xml_data_utf8,
        file_name=new_filename,
        mime="application/xml"
        )


def compare_original_and_updated_data(xml_table, updated_data):
    user_data = updated_data.to_dict('records')
    output = []
    for rec in xml_table:
        for user_rec in user_data:
            if rec['moodle_id'] == user_rec['moodle_id']:
                if rec['questiontext'] != user_rec['questiontext'] or rec['option1'] != user_rec['option1'] or rec['option2'] != user_rec['option2'] or rec['option3'] != user_rec['option3'] or rec['option4'] != user_rec['option4'] or rec['soln'] != user_rec['soln'] or rec['incorrect_feedback'] != user_rec['incorrect_feedback']:
                   output.append(user_rec)

    return output
# Main
#st.header("Program to Update Quiz Data")
#st.title("Please upload XML file to display/edit the data")
xml_table, new_filename = get_data_from_xml()       #Get the data from the XML file
if len(xml_table) > 0 :
    display_data(xml_table)                             #Display the original data
    #updated_data = edit_data(xml_table)                 #Edit the data
    # final_updated_data = compare_original_and_updated_data(xml_table, updated_data)
    # if final_updated_data != []:
    #     st.write("### Updated Data:")
    #     st.dataframe(final_updated_data)
    #     xml_data = updated_data.to_dict('records')          #Converting the updated data dataframe to dictionary format
    #     create_xml(xml_data,new_filename)               #Once submitted, the updated XML file is created and saved in the folder path mentioned
