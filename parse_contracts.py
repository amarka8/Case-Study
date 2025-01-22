from grobid_client.grobid_client import GrobidClient

if __name__ == "__main__":
    client = GrobidClient(config_path="./config.json")
    client.process("processFulltextDocument", "./xmad-contracts", output="./parsed-test-contracts/xmad", consolidate_citations=True, tei_coordinates=True)
    client.process("processFulltextDocument", "./sec_data/2024/QTR1", output="./parsed-test-contracts/2024_q_1 ", consolidate_citations=True, tei_coordinates=True)
    