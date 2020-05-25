# Configure models
ATTN_MODEL = 'dot'
#ATTN_MODEL = 'general'
#ATTN_MODEL = 'concat'
HIDDEN_SIZE = 500
ENCODER_N_LAYERS = 2
DECODER_N_LAYERS = 2
DROPOUT = 0.1
BATCH_SIZE = 64

# Configure training/optimization
CLIP = 50.0
TEACHER_FORCING_RATIO = 1.0
LEARNING_RATE = 0.0001
DECODER_LEARNIN_RATIO = 5.0
N_ITERATION = 1
PRINT_EVERY = 1
SAVE_EVERY = 1

# Set checkpoint to load from; set to None if starting from scratch
# LOADFILENAME = None
LOADFILENAME = 'data/state/1_checkpoint.pt'
CHECKPOINT_ITER = 4000
