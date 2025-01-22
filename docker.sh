docker pull grobid/grobid:0.8.1
docker run --rm --gpus '"device=1,2"' --init --ulimit core=0 -p 8070:8070 -p 8081:8071 grobid/grobid:0.8.1
# grobid_client --input ./xmad-contracts --output ./parsed-test-contracts/xmad processFulltextDocument
# grobid_client --input ./sec_data/2024/QTR1 --output ./parsed-test-contracts/2024_q_1 processFulltextDocument
