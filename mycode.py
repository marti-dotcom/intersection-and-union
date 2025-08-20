"""
Intersection & Union of BED4 Intervals (CLI)

Author: Martina Debnath
GitHub: https://github.com/marti-dotcom
License: MIT
"""
__author__ = "Martina Debnath"
__version__ = "1.0.0"
__license__ = "MIT"


import argparse
import os 
import sys  


def read_bed_file(filename): #Reads a BED4 file
    
    if not os.path.exists(filename):  #checking if the file is actually at the path
        sys.exit(f"Error because the input file '{filename}' doesnt exist.") 
    intervals = []  

    with open(filename, 'r') as f:    
        for lineno, line in enumerate(f, 1):       #Loops through each line of the file, whilst also keeping track of line number (starting from 1).
            line = line.strip()                    #Removes any extra whitespace from the ends of the line
            if not line or line.startswith('#'):   # Skips blank lines or comment lines that start with a #
                continue
            parts = line.split()        #Splits the line into individual columns based on tabs

            if len(parts) < 3:     #Checks if the bed4 file has are fewer than 3 parts (columns) after splitting
                print(f"Warning: There is an incorrect line {lineno} in '{filename}': '{line}', so skipping.", file=sys.stderr) #If the line is incorrect, it prints a warning and skips that line.
                continue            
            chrom = parts[0]  
            try:
                start = int(parts[1]) #Makes sure the second (start position) and third (end position) parts into integers
                end   = int(parts[2])
            except ValueError:
                print(f"Warning: Non-integer start/end on line {lineno} in '{filename}', skipping.", file=sys.stderr)
                continue  
           
            if start > end:     #Checks if the start position is greater than the end position (which can happen in BED files due to inverted intervals) and swaps them 
                start, end = end, start
        
            name = parts[3] if len(parts) > 3 else '.'  #If there is a fourth column (the name), it assigns that to name. If there is no fourth column, it assigns a dot
            intervals.append((chrom, start, end, name)) #Adds tuple to the intervals list
    return intervals


def find_intersections(intervals1, intervals2): #takes two sets of intervals (from two BED files) and finds where they overlap, returning list

    results = [] 
    for chrom1, s1, e1, name1 in intervals1:   #for interval1 (first bed4 file) it does a loop looking at chromosome, start, end, and name
        for chrom2, s2, e2, _ in intervals2:    
            if chrom1 == chrom2 and s1 < e2 and s2 < e1:  #checks if the intervals are on the same chromosome and if they overlap
                istart = max(s1, s2)     #calculates the overlap region between the two intervals
                iend   = min(e1, e2)        
                if istart < iend: #just to double check
                    results.append((chrom1, istart, iend, name1))  #If the overlap is valid (istart < iend), it appends the overlapping interval to the results list
    return results 


def find_unions(intervals1, intervals2): #merges the two files from min of one file to max of another, You want to group and merge intervals by name.

    by_name = {}        #starts an empty dictionary to store intervals by feature name
    for chrom, start, end, name in intervals1 + intervals2:       #Loops through all intervals in both intervals1 and intervals2.
        if name not in by_name:          
            by_name[name] = {'chrom': chrom, 'start': start, 'end': end, 'count': 1}
        else:        #but if the name is already in the dictionary
            entry = by_name[name]  #you fetch the one you currently already have

            if entry['chrom'] != chrom:   #It checks if the chromosome is the same
                entry['invalid'] = True   #if not, it marks as invalid
            else:
                entry['start'] = min(entry['start'], start)  #otherwise if the chromosome is the same
                entry['end']   = max(entry['end'],   end) #Otherwise, it extends the start and end to include the current interval’s range
            entry['count'] += 1  
    results = []    #Loops through the dictionary and only adds valid intervals to the results list

    for name, entry in by_name.items():
        if entry.get('invalid'): #It skips any intervals that were marked as invalid (those that span different chromosomes)
            continue
        results.append((entry['chrom'], entry['start'], entry['end'], name)) 
    return results


def write_bed_file(filename, intervals):  #to write the processed intervals to a new BED4 file

    with open(filename, 'w') as f:  #Opens the output file in writing mode
        for chrom, start, end, name in intervals:
            f.write(f"{chrom}\t{start}\t{end}\t{name}\n") #Writes each interval as a tab separated line


def main():
    parser = argparse.ArgumentParser(    #Starts the ArgumentParser to handle command-line arguments from the terminal
        description='Processing the union or intersection on the two BED4 files.')
    parser.add_argument(
        'operation', choices=['union', 'isec'], 
        help='Choose if you want to perform union or intersection') #Adds an argument for the operation type (union or isec)
    parser.add_argument(    
        'input1', help='First input BED4 file')
    parser.add_argument(
        'input2', help='Second input BED4 file') 
    parser.add_argument(
        'output', help='Output BED file') 
    args = parser.parse_args()  

    intervals1 = read_bed_file(args.input1)  #Reads the two input files and loads into intervals1 and intervals2
    intervals2 = read_bed_file(args.input2)

    if args.operation == 'union': #If the operation is union, it calls find_unions and prints the result
        result = find_unions(intervals1, intervals2)
        print(f"Merging by name union: {len(result)} features → {args.output}")
    else:   
        result = find_intersections(intervals1, intervals2)
        print(f"Found intersections: {len(result)} overlaps → {args.output}")

    write_bed_file(args.output, result)  #Writes the result (from result) to the output file


if __name__ == '__main__':  #Makes sure the main() function is only done if the script is run directly, not imported as a module into another python code programme
    main()



