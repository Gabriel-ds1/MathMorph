# main.py

from pipeline import SentenceProcessor

if __name__ == "__main__":
    processor = SentenceProcessor(step_val=0, stage_val=0, print_val=0)
    processor.run()
    processor.save_results()