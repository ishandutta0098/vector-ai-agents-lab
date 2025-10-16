conda activate orion

python -m main \
    --prompt "Change the checkpoint path to cifar_trained.ckpt in the script src/basic/level_05_pretrained_model/pretrained_model.py and improve the code" \
    --repo-url "https://github.com/ishandutta0098/zero-to-lightning" \
    --no-venv \
    --no-testing \
    --conda-env "ml"