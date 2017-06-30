from isee_engine.mintnet.hmax.hmouse import hmouse

def hmouse_test():

    # Instantiate model with configuration directory
    hm = hmouse('hmax')

    # Train the model if the train state says so
    hm.train()  

    #  run a test image and generate output
    hm.generate_output()

if __name__=='__main__':

    hmouse_test()