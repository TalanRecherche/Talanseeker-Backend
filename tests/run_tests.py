"""Created by agarc at 06/10/2023
Features:
"""

if __name__ == "__main__":
    #Run pytest excluding tests with the @pytest.mark.skip_this decorator
    #@pytest.mark.skip_this is used for tests that require calls to openai API
    #pytest.main(["-m", "not skip_this", '-vvvv'])

    #Use this line to run all tests, including those which call openai API
    #pytest.main(["-m", '-vvvv'])
