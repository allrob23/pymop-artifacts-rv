import xml.parsers.expat

def test_ok_1():
    # Create an XML parser object
    p = xml.parsers.expat.ParserCreate()

    # Parse the XML document in chunks
    p.Parse('<root>', False)  # Parsing first chunk
    p.Parse('<child>data</child>', False)  # Parsing second chunk
    p.Parse('</root>', True)  # CORRECT USAGE: Parsing final chunk and correctly indicating it's the end

def test_ok_2():
    p = xml.parsers.expat.ParserCreate()
    p.Parse('<root>', False)
    p.Parse('<child>data</child>', False) 
    # This will throw an error because the XML is invalid and this is the last chunk
    p.Parse('<root>', True)

def test_violation_1():
    p = xml.parsers.expat.ParserCreate()
    p.Parse('<root>', False)
    p.Parse('<child>data</child>', False) 
    p.Parse('</root>', False) # Violation: not indicating that it is the final chunk

def test_violation_2():
    p = xml.parsers.expat.ParserCreate()
    p.Parse('<root>', False)
    p.Parse('<child>data</child>', False) 
    # Note that the XML is invalid because here we need
    # </root> instead of <root> however, it is not checked
    # because is_final = False
    p.Parse('<root>', False)


# The spec XMLParser_ParseMustFinalize uses the `end` event from pythonmop
# because of that, the violation is only detected after the end of the last test
expected_violations_A = 2
expected_violations_B = [test_violation_2, test_violation_2]
expected_violations_C = [test_violation_2, test_violation_2]
expected_violations_C_plus = [test_violation_2, test_violation_2]
expected_violations_D = [test_violation_2, test_violation_2]
