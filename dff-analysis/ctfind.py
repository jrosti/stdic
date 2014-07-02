    
if __name__=="__main__":
    
    from ctfinders.ctfinder import CTFinderFactory
    from ctfinders.criterions.criterion import CriterionFactory
    import sys
    
    data = sys.argv[1]
    findercriterion = sys.argv[2]
    
    criterionclass = CriterionFactory().getCriterionClass(findercriterion)
    
    ctfinder = CTFinderFactory().getCTFinder(data, criterionclass)

    output = sys.argv[3]
    ctfinder.getCrackTips(output)