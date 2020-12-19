
# CONFIG -----------------------------------------------------------------------------------------------------------#

# Here are the input and output data paths (Note: you can override wav_path in preprocess.py)
wav_path = '/path/to/wav_files/'
data_path = 'data/'

# model ids are separate - that way you can use a new tts with an old wavernn and vice versa
# NB: expect undefined behaviour if models were trained on different DSP settings
voc_model_id = 'ljspeech_raw'
tts_model_id = 'ljspeech_tts'

# set this to True if you are only interested in WaveRNN
ignore_tts = False


# DSP --------------------------------------------------------------------------------------------------------------#

# Settings for all models
sample_rate = 22050
n_fft = 2048
fft_bins = n_fft // 2 + 1
num_mels = 80
hop_length = 256                    # 12.5ms - in line with Tacotron 2 paper
win_length = 1024                   # 50ms - same reason as above
fmin = 0
fmax = 8000
bits = 9                            # bit depth of signal
mu_law = True                       # Recommended to suppress noise if using raw bits in hp.voc_mode below
peak_norm = False                   # Normalise to the peak of each wav file


# GENERAL TRAINING ----------------------------------------------------------------------------------------------------------#

seed = 42
n_val = 200                         # num validatino samples

# WAVERNN / VOCODER ------------------------------------------------------------------------------------------------#


# Model Hparams
voc_mode = 'RAW'                    # either 'RAW' (softmax on raw bits) or 'MOL' (sample from mixture of logistics)
voc_upsample_factors = (4, 8, 8)   # NB - this needs to correctly factorise hop_length
voc_rnn_dims = 512
voc_fc_dims = 512
voc_compute_dims = 128
voc_res_out_dims = 128
voc_res_blocks = 10

# Training

voc_schedule = [(1e-4,  300_000,  32),        # progressive training schedule
                (2e-5,  2_000_000,  32)]      # (lr, step, batch_size)

voc_checkpoint_every = 25_000
voc_gen_samples_every = 5000        # how often to generate samples for cherry-picking models
voc_gen_num_samples = 3             # number of samples to generate for cherry-picking models
voc_keep_top_k = 3                  # how many top performing models to keep
voc_pad = 2                         # this will pad the input so that the resnet can 'see' wider than input length
voc_seq_len = hop_length * 5        # must be a multiple of hop_length
voc_clip_grad_norm = 4              # set to None if no gradient clipping needed

# Generating / Synthesizing
voc_gen_batched = True              # very fast (realtime+) single utterance batched generation
voc_target = 11_000                 # target number of samples to be generated in each batch entry
voc_overlap = 550                   # number of samples for crossfading between batches



# TACOTRON TTS -----------------------------------------------------------------------------------------------------#

# Model Hparams
tts_embed_dims = 256                # embedding dimension for the graphemes/phoneme inputs
tts_encoder_dims = 128
tts_decoder_dims = 256
tts_postnet_dims = 128
tts_encoder_K = 16
tts_lstm_dims = 512
tts_postnet_K = 8
tts_num_highways = 4
tts_dropout = 0.5
language = 'en'
tts_cleaner_name = 'english_cleaners'
tts_stop_threshold = -11           # Value below which audio generation ends.
                                    # For example, for a range of [-4, 4], this
                                    # will terminate the sequence at the first
                                    # frame that has all values < -3.4

# Training

tts_schedule = [(10,  1e-3,  10_000,  32),   # progressive training schedule
                (5,  1e-4, 20_000,  16),   # (r, lr, step, batch_size)
                (2,  1e-4, 30_000,  8),
                (1,  1e-4, 50_000,  8)]

tts_max_mel_len = 1250              # if you have a couple of extremely long spectrograms you might want to use this
tts_clip_grad_norm = 1.0            # clips the gradient norm to prevent explosion - set to None if not needed
tts_checkpoint_every = 10_000        # checkpoints the model every X steps
tts_plot_every = 1000

# ------------------------------------------------------------------------------------------------------------------#


# FORWARD TACOTRON -----------------------------------------------------------------------------------------------------#


# Model Hparams
forward_embed_dims = 256                # embedding dimension for the graphemes/phoneme inputs
forward_prenet_dims = 256
forward_postnet_dims = 256
forward_durpred_conv_dims = 256
forward_durpred_rnn_dims = 64
forward_durpred_dropout = 0.5
forward_prenet_K = 16
forward_postnet_K = 8
forward_rnn_dims = 512
forward_num_highways = 4
forward_dropout = 0.1

# Training

forward_schedule = [(1e-4, 10_000,  32),    # progressive training schedule
                    (1e-4, 300_000,  32)]   # (lr, step, batch_size)

forward_max_mel_len = 1250              # if you have a couple of extremely long spectrograms you might want to use this
forward_clip_grad_norm = 1.0            # clips the gradient norm to prevent explosion - set to None if not needed
forward_checkpoint_every = 10_000        # checkpoints the model every X steps
forward_plot_every = 1000

# ------------------------------------------------------------------------------------------------------------------#

