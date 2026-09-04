from jd_processor import  extract_sections, jd_read ,clean_jd
jd = jd_read("C:\\Users\\SAMA\\Downloads\\resume-ai\\job\\job_description.txt")
requirements, responsibilities = extract_sections(jd)

print("REQUIREMENTS:")
for item in requirements:
    print("-", item)

print("\nRESPONSIBILITIES:")
for item in responsibilities:
    print("-", item)


