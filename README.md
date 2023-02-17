# samples

You may be able to run this locally if you're able to navigate the dependencies, otherwise it works fine on colab (link below). 

See below for a detailed walk through. Thanks kindly to Reviewer 2 for the push needed to clean up this code.


# Colab Notes

You'll have to add the structures.sdf to the colab server to get the basic functionalities to work, and the tensorflow model in model.zip to get the VAE functionalities to work.

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1N0SOHK37Ukv_9swhTsKK_Br0zOwCMqFL?usp=sharing)


# Trained Model From the Paper

Instead, here's a google drive link to the file: https://drive.google.com/file/d/1zazFRO8QpfBK_c4uZ3RRpuOwfQASK83R/view?usp=sharing

Or on Zenodo: https://doi.org/10.5281/zenodo.6391612


# As reported on ChemRxiv: 

https://chemrxiv.org/engage/chemrxiv/article-details/6236172dd75627dbfb1e0c92



# Installation
## Installation of virtual environment

We first create a virtual environment to avoid dealing with other packages installed in the system:

Test folder:
$ mkdir Test && cd Test

If you are on an arm64 apple silcon system, it is necessary to use Python 3.9 for compatability reasons.

We create a virtual environment:
$ python3.9 -m venv samples_venv

And activate it:
$ source samples_venv/bin/activate

Upgrade pip if it hasn't been already:
$ (samples_venv) pip install --upgrade pip


## Installation of dependencies and packages:
First install jupyter lab:
(samples_venv) $ pip install jupyterlab

In this order, install selfies:
(samples_venv) $ pip install selfies===1.0.0

Then rdkit-pypi:
(samples_venv) $ pip install rdkit-pypi

We install python-rtmidi, llvmlite, and numba:

(samples_venv) $ pip install python-rtmidi
(samples_venv) $ pip install llvmlite
(samples_venv) $ pip install numba

If you are on an arm64 apple silcon setup, we need to manually install a compatible tensorflow verison:
(samples_venv) $ pip install tensorflow-macos

And then git clone magenta:
(samples_venv) $ git clone https://github.com/magenta/magenta.git

We go to the folder:
(samples_venv) $ cd magenta

And modify the setup.py commenting out the packages we install manually:
\# 'python-rtmidi == 1.1.2'
\# 'librosa == 0.7.2'
\# 'numba == 0.49.1

Comment out tensorflow if it was installed manually earlier:
\# 'tensorflow === 2.9.1'


We now install the magenta package:
$ python -m pip install .


Now the rest of the python packages:
(samples_venv) $ pip install music21===5.5.0
(samples_venv) $ pip install matplotlib
(samples_venv) $ pip install scikit-learn

Finally, you may have to install this specific version of numpy if you are running into compatability issues unresolved by pip
(samples_venv) $ pip install numpy==1.23.5

And this works! You have now successfully installed all the python packages.
You can test it by:
(samples_venv) $ python
(samples_venv) $ >> import magenta


## Setting up the system:
(samples_venv) $ cd ..
(samples_venv) $ mkdir test
(samples_venv) $ mkdir wav
Download the model.zip from Zenodo:
https://zenodo.org/record/6395321
And extract it.

Lastly, we need fluidsynth, a program that converts midi to wav.
Fluidsynth is a real-time software synthesizer. You can read more about it here:
https://wiki.archlinux.org/title/FluidSynth
In archlinux-based machines, it can be installed as:
$ pacman -S fluidsynth
Or with brew:
$ brew install fluid-synth

A SoundFont is also needed. Here is a list of them:
https://wiki.archlinux.org/title/MIDI#List_of_SoundFonts

The FatBoy works pretty well and can be installed through the AUR repositories as:
$ yay -Ss soundfont-fatboy

Alternatively you can directly download the soundfont here:
curl -O -L 'https://web.archive.org/web/20220124174052/https://dl.fatboy.site/FatBoy-latest.7z'

# Explanation of the script:

## First part of the script:

After importing the necessary python packages, there are two main functions:

The create_midi_file function will create the midi file from the SMILES string. This string is
hardcoded and declared in the `smiles` variable.
Additionally, we need to declare the `filename` variable, which will give the rootname to our
files.

The create_wav_spectra function will call the fluidsynth program and convert our midi files
to wav and create the frequency graph.

The fluidsynth command must now be hardcoded in the `samples.py` script as:

```
fluidsynth -ni font.sf2 test/"+filename+".mid -F wav/"+filename+".wav -r 44100
```

You need to replace `font.sf2` by the directory where the `soundfonts` `sf2` are listed.
In case of having installed fatboy soundfont, this is the command that you should use in the
samples.py script:

```
fluidsynth -ni /usr/share/soundfonts/FatBoy.sf2 test/9.mid -F wav/9.wav -r 44100
```

or just 

```
fluidsynth -ni FatBoy-v0.790.sf2 test/9.mid -F wav/9.wav -r 44100
```

if downloaded directly into the working directory


## Third part of the script:
Running the MusicVAE functions.

Ensure the model checkpoint path is correctly pointing to the right directory. 

MIDI sequences in the "test" directory will be input into the model. I suggest saving two molecule encoded MIDI sequences using the functions above.

There is a max length of 16 selfie tokens for the provided model.

The function interpolate takes two MIDI sequences and returns a MIDI sequence that is "in between" the input sequences.

This works by using the pretrained VAE to map the input sequences to encoder latent space. Point between these embeddings are sampled.

The seq_to_smiles function converts an input MIDI sequence into a SMILES encoded molecule.

Run the second block of code to return "interpolated" molecules and generate a piano roll graphic of the output.



## Fourth part of the script:
General informatics as shown in the paper.

The first figure shows a bar chart that reflects the distribution of molecules and the key in which they are encoded in.

The bars are colored by their estimated "druglikedness" - a decimal between 0 and 1 reflecting how well the molecule matches druglike properties.

This is relevant since key the molecule is encoded into is dictated by its physicochemical properties – which also cooralate with estimated druglikedness (QED).

With this encoding scheme, the less druglike a molecule is, the more likely it will be encoded into a unpopular key (as determined by the distribution of keys in songs listed on Spotify)

The encoding was intended to bin the most druglike molecules into the key of G, which happens to be the most popular key found in music listed on Spotify.

Indeed the majority of drugs listed on DrugBank do fall into G. Printed are the keys, the number of compounds from DrugBank found encoded in that key, and the mean QED of that bin. See Figure S1.



For the second graphic, we collect the drugs listed on DrugBank and encode the whole dataset into a 512 bit fingerprint – an array of 0s and 1s reflecting the structure of the molecule.

In this particular instance, the Morgan Fingerprint as provided by RDKit is utilized. This matrix is reduced into two dimensions via t-SNE, which requires a numpy array as its input.

We group each point by its key to allow us to easily color each key in the plot. We reduce the transparency of the first bin (G, the most populous) to improve clarity.

## Fifth part of the script:
Finally, this block of code exemplfies how to convert a user generated sequence of MIDI notes into a molecule. The example as shown in the paper is given here.
