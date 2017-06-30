
def test_basic():

    import sys
    import os
    sys.path.append(os.path.join(sys.path[0],'../..'))
    import isee_engine as package
    reload(package)
    
if __name__ == '__main__':                                    # pragma: no cover
    test_basic()                                              # pragma: no cover