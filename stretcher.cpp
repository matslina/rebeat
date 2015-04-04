#include <stdlib.h>
#include <SoundTouch.h>

extern "C" {

using namespace soundtouch;

typedef struct stretcher_t {
  SoundTouch *st;
  float *signal;
  uint nsamples;
  uint nchannels;
  uint samplerate;
  uint samplewidth;
  char *out;
  size_t out_size;
  size_t out_len;
} stretcher_t;

stretcher_t *stretcher_new(char *data, size_t size,
			   uint nchans, uint srate, uint swidth) {
  stretcher_t *s;
  int i;
  float factor;

  s = new stretcher_t;
  s->nsamples = size / (swidth * nchans);
  s->nchannels = nchans;
  s->samplerate = srate;
  s->samplewidth = swidth;
  s->out = (char *)malloc(size);
  s->out_size = size;
  s->out_len = 0;

  s->st = new SoundTouch();
  s->st->setChannels(s->nchannels);
  s->st->setSampleRate(s->samplerate);

  s->signal = (float *)malloc(sizeof(float) * s->nsamples);
  if (s->samplewidth == 2)
    for (i = 0, factor = 1 << 15; i < s->nsamples; i++)
      s->signal[i] = ((int16_t *)data)[i] / factor;

  return s;
}

void stretcher_stretch(stretcher_t *s, float duration) {
  float *samples;
  int nsamples, i;

  s->st->setTempo((s->nsamples / s->samplerate) / duration);
  s->st->putSamples(s->signal, s->nsamples);
  s->st->flush();
  nsamples = s->st->numSamples();
  samples = (float *)malloc(sizeof(float) * nsamples);
  s->st->receiveSamples(samples, nsamples);

  if (s->out_size < nsamples * s->samplewidth) {
    free(s->out);
    s->out_size = nsamples *  s->samplewidth;
    s->out = (char *)malloc(s->out_size);
  }

  for (i = 0; i < nsamples; i++)
    ((int16_t *)s->out)[i] = samples[i] * 32768;
  s->out_len = nsamples * s->samplewidth;

  free(samples);
}

int stretcher_length(stretcher_t *s) {
  return s->out_len;
}

void *stretcher_data(stretcher_t *s) {
  return s->out;
}

}
