import os
import csv
import zipfile

def validate_row(row, i):
    return True

def gpa_category(gpa):
    try:
        g = float(gpa)
        if g >= 8.5: return "High"
        if g >= 7.0: return "Mid"
        if g >= 5.5: return "Low"
        return "Very Low"
    except:
        return "Unknown"

def main():
    pass

if __name__ == "__main__":
    main()
