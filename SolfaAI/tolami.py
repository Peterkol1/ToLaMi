import music21

SOLFA_MAP = {
    0: 'd', 1: 'de', 2: 'r', 3: 'ma', 4: 'm', 5: 'f', 6: 'fi',
    7: 's', 8: 'le', 9: 'l', 10: 'ta', 11: 't'
}

def get_solfa_and_octave(tonic_pitch, target_pitch):
    interval = music21.interval.Interval(noteStart=tonic_pitch, noteEnd=target_pitch)
    semitones = interval.semitones
    
    base_interval = semitones % 12
    syllable = SOLFA_MAP.get(base_interval, '?')
    
    octave_shift = semitones // 12
    if octave_shift > 0:
        syllable += "'" * octave_shift
    elif octave_shift < 0:
        syllable += "," * abs(octave_shift)
        
    return syllable

def convert_midi_to_solfa_v4(midi_file_path):
    print(f"Loading and analyzing: {midi_file_path}...\n")
    
    try:
        score = music21.converter.parse(midi_file_path)
    except Exception as e:
        return f"Error reading MIDI file: {e}"

    key = score.analyze('key')
    tonic = key.tonic
    time_sig = score.getTimeSignatures()[0].ratioString if score.getTimeSignatures() else '4/4'
    
    print(f"🎵 Detected Key: {key.tonic.name} {key.mode.capitalize()}")
    print(f"⏱  Time Signature: {time_sig}")
    print("-" * 50)

    unified_score = score.chordify()
    
    final_sheet = []
    
    for measure in unified_score.getElementsByClass(music21.stream.Measure):
        measure_solfa = []
        
        for event in measure.notesAndRests:
            if event.isRest:
                continue
            elif event.isNote:
                syllable = get_solfa_and_octave(tonic, event.pitch)
                measure_solfa.append(syllable)
            elif event.isChord:
                # NEW CHORD LOGIC: Get all notes in the chord!
                chord_syllables = []
                # music21 automatically sorts pitches from lowest to highest
                for pitch in event.pitches:
                    syllable = get_solfa_and_octave(tonic, pitch)
                    chord_syllables.append(syllable)
                
                # Group them together in brackets, joined by a dot
                chord_string = "[" + ".".join(chord_syllables) + "]"
                measure_solfa.append(chord_string)
        
        if measure_solfa:
            final_sheet.append(" ".join(measure_solfa))

    arranged_output = ""
    for i in range(0, len(final_sheet), 4):
        chunk = " | ".join(final_sheet[i:i+4])
        arranged_output += f"| {chunk} |\n"

    return arranged_output

if __name__ == "__main__":
    test_file = "bach_846.mid" 
    
    result = convert_midi_to_solfa_v4(test_file)
    print("\n🎼 V4 Tonic Sol-fa Extraction (with Chords):")
    print(result)