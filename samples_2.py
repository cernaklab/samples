from rdkit import Chem
import selfies
import numpy as np
import matplotlib.pyplot as plt
import wave
import os
from rdkit import RDLogger
RDLogger.DisableLog('rdApp.*')                                                                                                                                                           


def getHashes():
  suppl = Chem.SDMolSupplier('structures.sdf')
  selfs = {}
  all_selfies = []
  for k in suppl:
      try:
          Chem.SanitizeMol(k)
          sel = selfies.encoder(Chem.MolToSmiles(k))
      except:
          continue
      if sel == None: continue
      all_selfies.append(sel)
      for j in list(selfies.split_selfies(sel)):
          if j not in selfs:
              selfs[j] = 0
          selfs[j] = selfs[j] + 1

  ranked_selfies_tokens = (sorted(selfs.items(), key=lambda item: item[1], reverse=True))

  note_to_shift = {}
  shift_to_note = {}
  # 2 2 1 2 2 2 1
  major_scale = [0,2,4,5,7,9,11, \
                 12,14,16,17,19,21,23, \
                 24,26,28,29,31,33,35, \
                 36,38,40,41,43,45,47, \
                 48,50,52,53,55,57,59]
  for i,k in enumerate(ranked_selfies_tokens[0:32]):
    note_to_shift[k[0]] = major_scale[i]
    shift_to_note[major_scale[i]] = k[0]
      
  valid_selfies_for_model = []
  for i,k in enumerate(all_selfies):
    tpl = list(selfies.split_selfies(k))
    not_good = False
    for tok in tpl:
      if tok not in note_to_shift:
        not_good = True
        break
    if not_good:
      continue
    else:
      valid_selfies_for_model.append(k)

  hashes = []
  for k in valid_selfies_for_model:
    hashes.append(hash_selfie(k))

  return hashes, note_to_shift, major_scale, shift_to_note, valid_selfies_for_model


def getAll(x): return [getMW(x), getLogP(x),getHBD(x),getHBA(x),getPSA(x),getROTB(x)]
def getLogP(x): return Chem.rdMolDescriptors.CalcCrippenDescriptors(x)[0]
def getMW(x): return Chem.Descriptors.MolWt(x)
def getHBD(x): return Chem.rdMolDescriptors.CalcNumHBD(x)
def getHBA(x): return Chem.rdMolDescriptors.CalcNumHBA(x)
def getPSA(x): return Chem.rdMolDescriptors.CalcTPSA(x)
def getROTB(x): return Chem.rdMolDescriptors.CalcNumRotatableBonds(x)
def getAROM(x): return Chem.rdMolDescriptors.CalcNumAromaticRings(x)
def getFSP3(x): return Chem.rdMolDescriptors.CalcFractionCSP3(x)
def getFC(x): return Chem.rdmolops.GetFormalCharge(x)
def getQED(x): return Chem.QED.qed(x)

def get_phys_prop_array(selfie):
  return getAll(Chem.MolFromSmiles(selfies.decoder(selfie)))

def hash_selfie(selfie):
  props = get_phys_prop_array(selfie)
  bit = 0
  for i,k in enumerate(props): bit = bit + k
  return bit

def hash_to_key(hash, hashMin, hashMax, keys):
  y = (((hash - hashMin) / (hashMax - hashMin)) * (len(keys) - 1)) + 0
  return keys[int(y)]

def create_wav_spectra(filename):
  signal_wave = wave.open('wav/'+str(filename)+'.wav', 'r')
  sample_rate = -1
  sig = np.frombuffer(signal_wave.readframes(sample_rate), dtype=np.int16)
  sig = sig[:]
  left, right = sig[0::2], sig[1::2]
  plt.figure(1)
  plot_a = plt.subplot(111)
  plot_a.plot(sig)
  plot_a.set_xlabel('sample rate * time')
  plot_a.set_ylabel('amplitude')
  xt = [plot_a.get_xticks()[1], (plot_a.get_xticks()[1]+plot_a.get_xticks()[-2])/2,plot_a.get_xticks()[-2]]
  plot_a.set_xticks(xt)
  plot_a.set_yticks([plot_a.get_yticks()[0], 0, plot_a.get_yticks()[-1]])
  plt.tight_layout()
  plt.savefig(str(filename)+".png",dpi=300)
