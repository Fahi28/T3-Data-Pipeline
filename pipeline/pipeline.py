"""Simple script to allow ETL pipeline to run in a single command."""
import extract
import transform
import load


if __name__ == "__main__":
    extract.main()
    transform.main()
    load.main()
