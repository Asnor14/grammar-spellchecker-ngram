"""
Rule-Based Grammar Checker module.
Handles specific grammar rules that statistical models can't reliably detect.
"""

import re
from typing import List, Dict, Tuple, Set


class GrammarRulesChecker:
    """
    Rule-based grammar checker for common grammar errors.
    
    Handles:
    - Subject-verb agreement
    - Verb tense consistency
    - Pronoun forms (it vs its)
    - Capitalization rules
    - Common grammar patterns
    """
    
    # Verb conjugations for common irregular verbs
    VERB_FORMS = {
        # base: (past, past_participle, present_3rd, present_participle)
        'buy': ('bought', 'bought', 'buys', 'buying'),
        'go': ('went', 'gone', 'goes', 'going'),
        'get': ('got', 'gotten', 'gets', 'getting'),
        'make': ('made', 'made', 'makes', 'making'),
        'take': ('took', 'taken', 'takes', 'taking'),
        'see': ('saw', 'seen', 'sees', 'seeing'),
        'come': ('came', 'come', 'comes', 'coming'),
        'know': ('knew', 'known', 'knows', 'knowing'),
        'think': ('thought', 'thought', 'thinks', 'thinking'),
        'say': ('said', 'said', 'says', 'saying'),
        'give': ('gave', 'given', 'gives', 'giving'),
        'find': ('found', 'found', 'finds', 'finding'),
        'tell': ('told', 'told', 'tells', 'telling'),
        'put': ('put', 'put', 'puts', 'putting'),
        'leave': ('left', 'left', 'leaves', 'leaving'),
        'do': ('did', 'done', 'does', 'doing'),
        'have': ('had', 'had', 'has', 'having'),
        'be': ('was', 'been', 'is', 'being'),
        'write': ('wrote', 'written', 'writes', 'writing'),
        'read': ('read', 'read', 'reads', 'reading'),
        'run': ('ran', 'run', 'runs', 'running'),
        'eat': ('ate', 'eaten', 'eats', 'eating'),
        'drink': ('drank', 'drunk', 'drinks', 'drinking'),
        'speak': ('spoke', 'spoken', 'speaks', 'speaking'),
        'drive': ('drove', 'driven', 'drives', 'driving'),
        'grow': ('grew', 'grown', 'grows', 'growing'),
        'throw': ('threw', 'thrown', 'throws', 'throwing'),
        'begin': ('began', 'begun', 'begins', 'beginning'),
        'sing': ('sang', 'sung', 'sings', 'singing'),
        'swim': ('swam', 'swum', 'swims', 'swimming'),
        'ring': ('rang', 'rung', 'rings', 'ringing'),
        'sit': ('sat', 'sat', 'sits', 'sitting'),
        'stand': ('stood', 'stood', 'stands', 'standing'),
        'lose': ('lost', 'lost', 'loses', 'losing'),
        'win': ('won', 'won', 'wins', 'winning'),
        'pay': ('paid', 'paid', 'pays', 'paying'),
        'meet': ('met', 'met', 'meets', 'meeting'),
        'send': ('sent', 'sent', 'sends', 'sending'),
        'build': ('built', 'built', 'builds', 'building'),
        'fall': ('fell', 'fallen', 'falls', 'falling'),
        'cut': ('cut', 'cut', 'cuts', 'cutting'),
        'keep': ('kept', 'kept', 'keeps', 'keeping'),
        'feel': ('felt', 'felt', 'feels', 'feeling'),
        'bring': ('brought', 'brought', 'brings', 'bringing'),
        'hold': ('held', 'held', 'holds', 'holding'),
        'catch': ('caught', 'caught', 'catches', 'catching'),
        'teach': ('taught', 'taught', 'teaches', 'teaching'),
        'understand': ('understood', 'understood', 'understands', 'understanding'),
        'break': ('broke', 'broken', 'breaks', 'breaking'),
        'spend': ('spent', 'spent', 'spends', 'spending'),
        'sleep': ('slept', 'slept', 'sleeps', 'sleeping'),
        'hear': ('heard', 'heard', 'hears', 'hearing'),
        'lead': ('led', 'led', 'leads', 'leading'),
        'fly': ('flew', 'flown', 'flies', 'flying'),
        'wear': ('wore', 'worn', 'wears', 'wearing'),
        'show': ('showed', 'shown', 'shows', 'showing'),
        'steal': ('stole', 'stolen', 'steals', 'stealing'),
        'hide': ('hid', 'hidden', 'hides', 'hiding'),
        'choose': ('chose', 'chosen', 'chooses', 'choosing'),
        'forget': ('forgot', 'forgotten', 'forgets', 'forgetting'),
        'rise': ('rose', 'risen', 'rises', 'rising'),
        'wake': ('woke', 'woken', 'wakes', 'waking'),
        'freeze': ('froze', 'frozen', 'freezes', 'freezing'),
        'shake': ('shook', 'shaken', 'shakes', 'shaking'),
        'draw': ('drew', 'drawn', 'draws', 'drawing'),
        'bite': ('bit', 'bitten', 'bites', 'biting'),
        'blow': ('blew', 'blown', 'blows', 'blowing'),
        # Regular verbs (add -ed for past)
        'drain': ('drained', 'drained', 'drains', 'draining'),
        'walk': ('walked', 'walked', 'walks', 'walking'),
        'talk': ('talked', 'talked', 'talks', 'talking'),
        'play': ('played', 'played', 'plays', 'playing'),
        'work': ('worked', 'worked', 'works', 'working'),
        'look': ('looked', 'looked', 'looks', 'looking'),
        'use': ('used', 'used', 'uses', 'using'),
        'try': ('tried', 'tried', 'tries', 'trying'),
        'ask': ('asked', 'asked', 'asks', 'asking'),
        'need': ('needed', 'needed', 'needs', 'needing'),
        'want': ('wanted', 'wanted', 'wants', 'wanting'),
        'move': ('moved', 'moved', 'moves', 'moving'),
        'live': ('lived', 'lived', 'lives', 'living'),
        'believe': ('believed', 'believed', 'believes', 'believing'),
        'happen': ('happened', 'happened', 'happens', 'happening'),
        'allow': ('allowed', 'allowed', 'allows', 'allowing'),
        'help': ('helped', 'helped', 'helps', 'helping'),
        'start': ('started', 'started', 'starts', 'starting'),
        'stop': ('stopped', 'stopped', 'stops', 'stopping'),
        'change': ('changed', 'changed', 'changes', 'changing'),
        'follow': ('followed', 'followed', 'follows', 'following'),
        'create': ('created', 'created', 'creates', 'creating'),
        'open': ('opened', 'opened', 'opens', 'opening'),
        'close': ('closed', 'closed', 'closes', 'closing'),
        'call': ('called', 'called', 'calls', 'calling'),
        'wait': ('waited', 'waited', 'waits', 'waiting'),
        'remain': ('remained', 'remained', 'remains', 'remaining'),
        # Additional common verbs
        'like': ('liked', 'liked', 'likes', 'liking'),
        'prefer': ('preferred', 'preferred', 'prefers', 'preferring'),
        'watch': ('watched', 'watched', 'watches', 'watching'),
        'enjoy': ('enjoyed', 'enjoyed', 'enjoys', 'enjoying'),
        'hate': ('hated', 'hated', 'hates', 'hating'),
        'love': ('loved', 'loved', 'loves', 'loving'),
        'finish': ('finished', 'finished', 'finishes', 'finishing'),
        'avoid': ('avoided', 'avoided', 'avoids', 'avoiding'),
        'consider': ('considered', 'considered', 'considers', 'considering'),
        'suggest': ('suggested', 'suggested', 'suggests', 'suggesting'),
        'recommend': ('recommended', 'recommended', 'recommends', 'recommending'),
        'decide': ('decided', 'decided', 'decides', 'deciding'),
        'agree': ('agreed', 'agreed', 'agrees', 'agreeing'),
        'refuse': ('refused', 'refused', 'refuses', 'refusing'),
        'promise': ('promised', 'promised', 'promises', 'promising'),
        'manage': ('managed', 'managed', 'manages', 'managing'),
        'hope': ('hoped', 'hoped', 'hopes', 'hoping'),
        'expect': ('expected', 'expected', 'expects', 'expecting'),
        'prepare': ('prepared', 'prepared', 'prepares', 'preparing'),
        'receive': ('received', 'received', 'receives', 'receiving'),
        'suppose': ('supposed', 'supposed', 'supposes', 'supposing'),
        # Daily Life & Study verbs
        'stay': ('stayed', 'stayed', 'stays', 'staying'),
        'plan': ('planned', 'planned', 'plans', 'planning'),
        'study': ('studied', 'studied', 'studies', 'studying'),
        'learn': ('learned', 'learned', 'learns', 'learning'),
        'listen': ('listened', 'listened', 'listens', 'listening'),
        'understand': ('understood', 'understood', 'understands', 'understanding'),
        'remember': ('remembered', 'remembered', 'remembers', 'remembering'),
        'wait': ('waited', 'waited', 'waits', 'waiting'),
        'visit': ('visited', 'visited', 'visits', 'visiting'),
        'travel': ('traveled', 'traveled', 'travels', 'traveling'),
        'worry': ('worried', 'worried', 'worries', 'worrying'),
        'clean': ('cleaned', 'cleaned', 'cleans', 'cleaning'),
        'cook': ('cooked', 'cooked', 'cooks', 'cooking'),
        'wash': ('washed', 'washed', 'washes', 'washing'),
        'fix': ('fixed', 'fixed', 'fixes', 'fixing'),
        'rain': ('rained', 'rained', 'rains', 'raining'),
        'snow': ('snowed', 'snowed', 'snows', 'snowing'),
        'relax': ('relaxed', 'relaxed', 'relaxes', 'relaxing'),
        'exercise': ('exercised', 'exercised', 'exercises', 'exercising'),
        'practice': ('practiced', 'practiced', 'practices', 'practicing'),
        'improve': ('improved', 'improved', 'improves', 'improving'),
    }
    
    # Singular subjects that require singular verbs
    SINGULAR_SUBJECTS = {
        'he', 'she', 'it', 'this', 'that', 'everyone', 'someone', 'anyone',
        'no one', 'nobody', 'everybody', 'somebody', 'anybody', 'each',
        'either', 'neither', 'one', 'battery', 'phone', 'brother', 'sister',
        'mother', 'father', 'car', 'computer', 'person', 'man', 'woman',
        'child', 'boy', 'girl', 'friend', 'teacher', 'student', 'dog', 'cat',
        # Uncountable nouns (always singular)
        'weather', 'news', 'traffic', 'information', 'advice', 'homework',
        'knowledge', 'furniture', 'equipment', 'luggage', 'baggage', 'money',
        'music', 'art', 'water', 'food', 'sugar', 'rice', 'evidence',
        'progress', 'research', 'work', 'time', 'air', 'health', 'love',
        'software', 'hardware', 'data', 'mathematics', 'physics', 'economics',
    }
    
    # Plural subjects that require plural verbs
    PLURAL_SUBJECTS = {
        'they', 'we', 'these', 'those', 'people', 'children', 'men', 'women',
        'friends', 'students', 'teachers', 'boys', 'girls', 'dogs', 'cats',
        'classmates', 'others', 'parents', 'relatives', 'siblings',
        'words', 'chairs', 'books', 'things',
    }
    
    # be verb forms
    BE_SINGULAR = {'is', 'was'}
    BE_PLURAL = {'are', 'were'}
    
    # Possessive pronouns mapping
    POSSESSIVE_MAP = {
        'it': 'its',
        'he': 'his', 
        'she': 'her',
        'they': 'their',
        'we': 'our',
        'i': 'my',
        'you': 'your',
    }
    
    def __init__(self):
        # Build reverse lookup for verb forms
        self.verb_base_lookup = {}
        for base, forms in self.VERB_FORMS.items():
            self.verb_base_lookup[base] = base
            for form in forms:
                if form not in self.verb_base_lookup:
                    self.verb_base_lookup[form] = base
    
    def check_text(self, text: str) -> List[Dict]:
        """
        Check text for grammar errors using rules.
        
        Args:
            text: Text to check
            
        Returns:
            List of error dictionaries
        """
        errors = []
        
        # GLOBAL PAST TENSE DETECTION - check entire text for past indicators
        past_indicators = {'yesterday', 'ago', 'last week', 'last month', 'last year', 
                          'last night', 'earlier', 'previously', 'before', 'already'}
        text_lower = text.lower()
        global_past_context = any(ind in text_lower for ind in past_indicators)
        
        # Check capitalization at sentence start
        errors.extend(self._check_sentence_capitalization(text))
        
        # Tokenize for word-level checking
        words = self._tokenize(text)
        
        # Check contractions (dont -> doesn't, etc.)
        errors.extend(self._check_contractions(text, words))
        
        # Check subject-verb agreement
        errors.extend(self._check_subject_verb_agreement(text, words))
        
        # Check possessive pronouns
        errors.extend(self._check_possessive_pronouns(text, words))
        
        # Check verb tense after past tense markers (with GLOBAL flag)
        errors.extend(self._check_verb_tense(text, words, force_past=global_past_context))
        
        # Check present participle with be verbs
        errors.extend(self._check_progressive_tense(text, words))
        
        # Check for 'say us' -> 'tell us' patterns
        errors.extend(self._check_say_to_tell(text, words))
        
        # Check for past tense verbs after conjunctions with past context
        errors.extend(self._check_past_tense_after_conjunction(text, words))
        
        # Check prefer/enjoy + gerund pattern
        errors.extend(self._check_gerund_patterns(text, words))
        
        # Check third person singular verb forms
        errors.extend(self._check_third_person_verbs(text, words))
        
        # Check plural nouns
        errors.extend(self._check_plural_nouns(text, words))
        
        # Check for past tense indicators after verbs (e.g., "win ... last week" -> "won")
        errors.extend(self._check_past_tense_indicator_after_verb(text, words))
        
        # Check for incorrect regularized past tense (e.g., "buyed" -> "bought")
        errors.extend(self._check_incorrect_regularized_past(text, words))
        
        # NEW RULE METHODS
        # Check pronoun "i" capitalization
        errors.extend(self._check_pronoun_capitalization(text, words))
        
        # Check double comparatives (more better -> better)
        errors.extend(self._check_double_comparatives(text, words))
        
        # Check infinitive patterns (forget bring -> forget to bring)
        errors.extend(self._check_infinitive_patterns(text, words))
        
        # Check article usage (a/an)
        errors.extend(self._check_articles(text, words))
        
        # Check adverb usage (runs quick -> runs quickly)
        errors.extend(self._check_adverbs(text, words))
        
        # Check redundant phrases (return back -> return)
        errors.extend(self._check_redundancy(text, words))
        
        # Check common preposition errors
        errors.extend(self._check_prepositions(text, words))
        
        # Check confused words (your/you're, their/there)
        errors.extend(self._check_confused_words(text, words))
        
        # Check quantifiers (no enough -> not enough)
        errors.extend(self._check_quantifiers(text, words))
        
        # Check prepositions with context (bring at home, angry to me)
        errors.extend(self._check_prepositions_context(text, words))
        
        # Check possessives with family/relation words (my brother car -> my brother's car)
        errors.extend(self._check_possessives_context(text, words))
        
        return errors
    
    def _tokenize(self, text: str) -> List[Tuple[str, int, int]]:
        """Tokenize text into words with positions."""
        tokens = []
        for match in re.finditer(r"\b\w+(?:'\w+)?\b", text):
            tokens.append((match.group().lower(), match.start(), match.end()))
        return tokens
    
    def _check_sentence_capitalization(self, text: str) -> List[Dict]:
        """Check if sentences start with capital letters."""
        errors = []
        
        # Check first word
        first_word = re.match(r'^\s*([a-z]+)', text)
        if first_word:
            word = first_word.group(1)
            start = first_word.start(1)
            end = first_word.end(1)
            errors.append({
                'type': 'grammar',
                'position': {'start': start, 'end': end},
                'original': word,
                'suggestion': word.capitalize(),
                'explanation': 'Sentences should start with a capital letter.',
                'sentenceIndex': 0,
            })
        
        # Check after sentence-ending punctuation
        for match in re.finditer(r'[.!?]\s+([a-z])', text):
            char = match.group(1)
            pos = match.start(1)
            errors.append({
                'type': 'grammar',
                'position': {'start': pos, 'end': pos + 1},
                'original': char,
                'suggestion': char.upper(),
                'explanation': 'Sentences should start with a capital letter.',
                'sentenceIndex': 0,
            })
        
        return errors
    
    def _check_subject_verb_agreement(self, text: str, words: List[Tuple[str, int, int]]) -> List[Dict]:
        """Check subject-verb agreement."""
        errors = []
        
        # Adverbs to skip when looking for subject
        adverbs_to_skip = {'already', 'just', 'always', 'never', 'really', 'often', 
                          'usually', 'sometimes', 'also', 'only', 'even', 'still'}
        
        for i, (word, start, end) in enumerate(words):
            # Check "it/battery/etc + are" → should be "is"
            if i > 0:
                prev_word = words[i - 1][0]
                
                # ADVERB SKIPPER: If prev_word is an adverb, look one more back
                actual_subject = prev_word
                if prev_word in adverbs_to_skip and i > 1:
                    actual_subject = words[i - 2][0]
                
                # Singular subject + are → is
                if actual_subject in self.SINGULAR_SUBJECTS and word == 'are':
                    errors.append({
                        'type': 'grammar',
                        'position': {'start': start, 'end': end},
                        'original': text[start:end],
                        'suggestion': 'is',
                        'explanation': f'Subject-verb agreement: "{actual_subject}" is singular and requires "is" not "are".',
                        'sentenceIndex': 0,
                    })
                
                # Singular subject + were → was
                elif actual_subject in self.SINGULAR_SUBJECTS and word == 'were':
                    errors.append({
                        'type': 'grammar',
                        'position': {'start': start, 'end': end},
                        'original': text[start:end],
                        'suggestion': 'was',
                        'explanation': f'Subject-verb agreement: "{actual_subject}" is singular and requires "was" not "were".',
                        'sentenceIndex': 0,
                    })
                
                # Plural subject + is → are
                elif actual_subject in self.PLURAL_SUBJECTS and word == 'is':
                    errors.append({
                        'type': 'grammar',
                        'position': {'start': start, 'end': end},
                        'original': text[start:end],
                        'suggestion': 'are',
                        'explanation': f'Subject-verb agreement: "{actual_subject}" is plural and requires "are" not "is".',
                        'sentenceIndex': 0,
                    })
                
                # Plural subject + was → were
                elif actual_subject in self.PLURAL_SUBJECTS and word == 'was':
                    # Check if next word is a verb - if so, skip (past tense check will handle)
                    next_word = words[i + 1][0] if i + 1 < len(words) else ""
                    past_indicators = {'yesterday', 'ago', 'last', 'before', 'earlier', 'previously', 'already'}
                    has_past_context = any(w[0] in past_indicators for w in words)
                    
                    # Only apply was→were if next word is NOT a verb in past context
                    if not (has_past_context and next_word in self.VERB_FORMS):
                        errors.append({
                            'type': 'grammar',
                            'position': {'start': start, 'end': end},
                            'original': text[start:end],
                            'suggestion': 'were',
                            'explanation': f'Subject-verb agreement: "{actual_subject}" is plural and requires "were" not "was".',
                            'sentenceIndex': 0,
                        })
        
        return errors
    
    def _check_possessive_pronouns(self, text: str, words: List[Tuple[str, int, int]]) -> List[Dict]:
        """Check possessive pronoun usage."""
        errors = []
        
        # Common nouns that follow possessive pronouns
        possession_indicators = {
            'battery', 'phone', 'car', 'house', 'name', 'book', 'life',
            'work', 'job', 'friend', 'family', 'mother', 'father', 'brother',
            'sister', 'hand', 'head', 'eye', 'heart', 'mind', 'way',
            'time', 'place', 'home', 'room', 'door', 'window', 'color',
        }
        
        for i, (word, start, end) in enumerate(words):
            if i < len(words) - 1:
                next_word = words[i + 1][0]
                
                # Check for "it battery" → "its battery"
                if word == 'it' and next_word in possession_indicators:
                    errors.append({
                        'type': 'grammar',
                        'position': {'start': start, 'end': end},
                        'original': text[start:end],
                        'suggestion': 'its',
                        'explanation': 'Use "its" (possessive) to show ownership, not "it".',
                        'sentenceIndex': 0,
                    })
                
                # Check for other pronouns before nouns
                elif word in self.POSSESSIVE_MAP and next_word in possession_indicators:
                    possessive = self.POSSESSIVE_MAP[word]
                    # Only flag if it's clearly wrong (not already possessive)
                    if word != possessive and not word.endswith('s') and word not in {'my', 'your', 'his', 'her', 'its', 'our', 'their'}:
                        errors.append({
                            'type': 'grammar',
                            'position': {'start': start, 'end': end},
                            'original': text[start:end],
                            'suggestion': possessive,
                            'explanation': f'Use "{possessive}" (possessive) to show ownership.',
                            'sentenceIndex': 0,
                        })
        
        return errors
    
    def _check_verb_tense(self, text: str, words: List[Tuple[str, int, int]], force_past: bool = False) -> List[Dict]:
        """Check verb tense consistency after past tense contexts."""
        errors = []
        
        # Past tense indicators
        past_indicators = {'yesterday', 'ago', 'last', 'before', 'earlier', 'previously', 'already'}
        
        # Words that indicate a completed action with ongoing result (use past tense)
        result_context = {'but', 'however', 'unfortunately', 'sadly', 'yet', 'still', 'now'}
        
        # Use global flag OR local detection
        has_past_context = force_past or any(w[0] in past_indicators for w in words)
        has_result_context = any(w[0] in result_context for w in words)
        
        # ALL subjects that can have main verbs after them
        all_subjects = {'i', 'we', 'you', 'they', 'he', 'she', 'it', 
                       'brother', 'sister', 'mother', 'father', 'friend', 'teacher', 'student'}
        all_subjects = all_subjects | self.SINGULAR_SUBJECTS | self.PLURAL_SUBJECTS
        
        # Adverbs to skip
        adverbs_to_skip = {'already', 'just', 'always', 'never', 'really', 'often', 
                          'usually', 'sometimes', 'also', 'only', 'even', 'still'}
        
        # Check for subject + base verb with past context
        for i, (word, start, end) in enumerate(words):
            # FIX: FIRST WORD CHECK - Don't skip first word if past context
            if i == 0 and has_past_context:
                # Check if first word is a base verb that needs past tense
                if word in self.VERB_FORMS and word not in {'be', 'is', 'are', 'was', 'were', 'have', 'has', 'had', 'do', 'does', 'did'}:
                    forms = self.VERB_FORMS[word]
                    past_form = forms[0]
                    
                    # Only flag if word is base form (key in dict) and not already past
                    if word != past_form:
                        errors.append({
                            'type': 'grammar',
                            'position': {'start': start, 'end': end},
                            'original': text[start:end],
                            'suggestion': past_form.capitalize() if start == 0 else past_form,
                            'explanation': f'Use past tense "{past_form}" because of past context.',
                            'sentenceIndex': 0,
                        })
                continue  # Move to next word after handling first word
            
            if i > 0:
                prev_word = words[i - 1][0]
                
                # ADVERB SKIPPER
                actual_subject = prev_word
                if prev_word in adverbs_to_skip and i > 1:
                    actual_subject = words[i - 2][0]
                
                # Check if there's result context after this word
                has_result_after = any(w[0] in result_context for w in words[i:])
                
                # If past context, force past tense for ANY subject + base verb
                if has_past_context or has_result_after:
                    if word in self.VERB_FORMS and word not in {'be', 'is', 'are', 'was', 'were', 'have', 'has', 'had'}:
                        forms = self.VERB_FORMS[word]
                        past_form = forms[0]  # past tense
                        
                        # INFINITIVE PROTECTION: Skip if verb is part of infinitive
                        # Check if prev_word is "to"
                        if prev_word == 'to':
                            continue
                        
                        # Check for modals before verb
                        modals = {'can', 'could', 'should', 'would', 'will', 'may', 'might', 'must'}
                        if prev_word in modals:
                            continue
                        
                        # Check for parallel infinitive: "to eat and drink"
                        # If prev_word is 'and'/'or' and words[i-2] is verb after 'to'
                        if prev_word in {'and', 'or'} and i > 2:
                            two_back = words[i - 2][0]
                            three_back = words[i - 3][0] if i > 3 else ''
                            if three_back == 'to' or two_back in modals:
                                continue
                        
                        # Only flag if: current word is base form AND subject precedes it
                        if actual_subject in all_subjects and word != past_form:
                            # Check it's base form (not already past)
                            if word == word:  # base form check (it's in VERB_FORMS as key)
                                errors.append({
                                    'type': 'grammar',
                                    'position': {'start': start, 'end': end},
                                    'original': text[start:end],
                                    'suggestion': past_form,
                                    'explanation': f'Use past tense "{past_form}" because of past context.',
                                    'sentenceIndex': 0,
                                })
                else:
                    # No past context - check third person singular requires -s
                    if actual_subject in {'brother', 'sister', 'he', 'she', 'it', 'mother', 'father', 'friend'}:
                        if word in self.VERB_FORMS:
                            forms = self.VERB_FORMS[word]
                            third_person_form = forms[2]  # present 3rd person
                            
                            if word != third_person_form:
                                errors.append({
                                    'type': 'grammar',
                                    'position': {'start': start, 'end': end},
                                    'original': text[start:end],
                                    'suggestion': third_person_form,
                                    'explanation': f'Subject-verb agreement: Use "{third_person_form}" with third-person singular subject.',
                                    'sentenceIndex': 0,
                                })
        
        return errors
    
    def _check_say_to_tell(self, text: str, words: List[Tuple[str, int, int]]) -> List[Dict]:
        """Check for incorrect usage of 'say' with object pronouns (should be 'tell')."""
        errors = []
        
        # say/said/says + object pronoun -> tell/told/tells + object pronoun
        say_forms = {
            'say': 'tell',
            'says': 'tells',
            'said': 'told',
            'saying': 'telling'
        }
        
        # Object pronouns that usually require 'tell' instead of 'say'
        object_pronouns = {'me', 'us', 'him', 'them', 'you', 'her'}
        
        for i, (word, start, end) in enumerate(words):
            # Check if current word is a form of 'say'
            if word in say_forms:
                # Check next word
                if i + 1 < len(words):
                    next_word = words[i + 1][0]
                    next_start = words[i + 1][1]
                    next_end = words[i + 1][2]
                    
                    if next_word in object_pronouns:
                        # Determine correct form (tell vs tells vs told)
                        suggestion = say_forms[word]
                        
                        # If suggesting 'tell', check if subject is singular (needs 'tells')
                        # Only if original word was 'say' (present)
                        if suggestion == 'tell':
                            # Look back for subject
                            prev_word = words[i - 1][0] if i > 0 else ""
                            # Simple check for known singular subjects
                            if prev_word in self.SINGULAR_SUBJECTS or prev_word in {'he', 'she', 'it'}:
                                suggestion = 'tells'
                        
                        errors.append({
                            'type': 'grammar',
                            'position': {'start': start, 'end': end},
                            'original': text[start:end],
                            'suggestion': suggestion,
                            'explanation': f'Use "{suggestion}" instead of "{word}" when followed by an object pronoun like "{next_word}".',
                            'sentenceIndex': 0,
                        })
        
        return errors

    def _check_progressive_tense(self, text: str, words: List[Tuple[str, int, int]]) -> List[Dict]:
        """Check for be + base verb patterns that should be progressive or past tense."""
        errors = []
        
        be_verbs = {'is', 'are', 'was', 'were', 'am'}
        past_be_verbs = {'was', 'were'}
        
        # Past tense indicators
        past_indicators = {'yesterday', 'ago', 'last', 'before', 'earlier', 'previously', 'already'}
        has_past_context = any(w[0] in past_indicators for w in words)
        
        for i, (word, start, end) in enumerate(words):
            if i > 0:
                prev_word = words[i - 1][0]
                
                if prev_word in be_verbs and word in self.VERB_FORMS:
                    forms = self.VERB_FORMS[word]
                    
                    # Skip certain verbs
                    if word in {'be', 'have', 'been'}:
                        continue
                    
                    # If we have past context and past be verb (was/were + go),
                    # suggest just the past tense verb (went) and remove was/were
                    if has_past_context and prev_word in past_be_verbs:
                        past_tense = forms[0]  # past tense
                        # Get the position of "was/were" to include it in the replacement
                        prev_start = words[i - 1][1]
                        errors.append({
                            'type': 'grammar',
                            'position': {'start': prev_start, 'end': end},  # Include was/were
                            'original': text[prev_start:end],  # "was go"
                            'suggestion': past_tense,  # "went"
                            'explanation': f'Use past tense "{past_tense}" instead of "{prev_word} {word}".',
                            'sentenceIndex': 0,
                        })
                    else:
                        # Normal progressive suggestion
                        progressive = forms[3]  # present participle (-ing form)
                        errors.append({
                            'type': 'grammar',
                            'position': {'start': start, 'end': end},
                            'original': text[start:end],
                            'suggestion': progressive,
                            'explanation': f'Use "{progressive}" (present participle) with "{prev_word}" for ongoing action.',
                            'sentenceIndex': 0,
                        })
        
        return errors
    
    def _check_past_tense_after_conjunction(self, text: str, words: List[Tuple[str, int, int]]) -> List[Dict]:
        """Check for verbs after conjunctions that should be past tense."""
        errors = []
        
        # Past tense indicators
        past_indicators = {'yesterday', 'ago', 'last', 'before', 'earlier', 'previously', 'already'}
        has_past_context = any(w[0] in past_indicators for w in words)
        
        if not has_past_context:
            return errors
        
        conjunctions = {'and', 'then'}
        
        for i, (word, start, end) in enumerate(words):
            if i > 0:
                prev_word = words[i - 1][0]
                
                # Check if previous word is a conjunction
                if prev_word in conjunctions and word in self.VERB_FORMS:
                    forms = self.VERB_FORMS[word]
                    past_tense = forms[0]  # past tense
                    
                    # Only suggest if current word is the base form
                    if word != past_tense:
                        errors.append({
                            'type': 'grammar',
                            'position': {'start': start, 'end': end},
                            'original': text[start:end],
                            'suggestion': past_tense,
                            'explanation': f'Use past tense "{past_tense}" to match the sentence context.',
                            'sentenceIndex': 0,
                        })
        
        return errors
    
    def _check_contractions(self, text: str, words: List[Tuple[str, int, int]]) -> List[Dict]:
        """Check for incorrect contractions and missing apostrophes."""
        errors = []
        
        # Common misspelled contractions with context
        # Format: misspelling -> {singular_subject: correction, plural_subject: correction}
        contraction_fixes = {
            'dont': {'default': "don't", 'third_singular': "doesn't"},
            'doesnt': {'default': "doesn't", 'third_singular': "doesn't"},
            'didnt': {'default': "didn't", 'third_singular': "didn't"},
            'wont': {'default': "won't", 'third_singular': "won't"},
            'cant': {'default': "can't", 'third_singular': "can't"},
            'couldnt': {'default': "couldn't", 'third_singular': "couldn't"},
            'wouldnt': {'default': "wouldn't", 'third_singular': "wouldn't"},
            'shouldnt': {'default': "shouldn't", 'third_singular': "shouldn't"},
            'isnt': {'default': "isn't", 'third_singular': "isn't"},
            'arent': {'default': "aren't", 'third_singular': "aren't"},
            'wasnt': {'default': "wasn't", 'third_singular': "wasn't"},
            'werent': {'default': "weren't", 'third_singular': "weren't"},
            'hasnt': {'default': "hasn't", 'third_singular': "hasn't"},
            'havent': {'default': "haven't", 'third_singular': "haven't"},
            'hadnt': {'default': "hadn't", 'third_singular': "hadn't"},
            'ive': {'default': "I've", 'third_singular': "I've"},
            'youve': {'default': "you've", 'third_singular': "you've"},
            'theyve': {'default': "they've", 'third_singular': "they've"},
            'weve': {'default': "we've", 'third_singular': "we've"},
            'hes': {'default': "he's", 'third_singular': "he's"},
            'shes': {'default': "she's", 'third_singular': "she's"},
            'its': {'default': "it's", 'third_singular': "it's"},  # Note: context matters for its vs it's
            'thats': {'default': "that's", 'third_singular': "that's"},
            'whats': {'default': "what's", 'third_singular': "what's"},
            'heres': {'default': "here's", 'third_singular': "here's"},
            'theres': {'default': "there's", 'third_singular': "there's"},
            'im': {'default': "I'm", 'third_singular': "I'm"},
            'youre': {'default': "you're", 'third_singular': "you're"},
            'theyre': {'default': "they're", 'third_singular': "they're"},
            'were': {'default': "we're", 'third_singular': "we're"},
            'ill': {'default': "I'll", 'third_singular': "I'll"},
            'youll': {'default': "you'll", 'third_singular': "you'll"},
            'theyll': {'default': "they'll", 'third_singular': "they'll"},
            'well': {'default': "we'll", 'third_singular': "we'll"},
            'hell': {'default': "he'll", 'third_singular': "he'll"},
            'shell': {'default': "she'll", 'third_singular': "she'll"},
            'itll': {'default': "it'll", 'third_singular': "it'll"},
        }
        
        for i, (word, start, end) in enumerate(words):
            if word in contraction_fixes:
                fixes = contraction_fixes[word]
                
                # Check previous word for subject
                prev_word = words[i - 1][0] if i > 0 else ""
                
                # Use third person singular form if subject is he/she/it or singular noun
                if prev_word in self.SINGULAR_SUBJECTS:
                    suggestion = fixes.get('third_singular', fixes['default'])
                else:
                    suggestion = fixes['default']
                
                # Special case: "dont" after "she/he/it" -> "doesn't"
                if word == 'dont' and prev_word in {'she', 'he', 'it'} | self.SINGULAR_SUBJECTS:
                    suggestion = "doesn't"
                
                errors.append({
                    'type': 'grammar',
                    'position': {'start': start, 'end': end},
                    'original': text[start:end],
                    'suggestion': suggestion,
                    'explanation': f'Use "{suggestion}" with proper apostrophe.',
                    'sentenceIndex': 0,
                })
        
        return errors
    
    def _check_gerund_patterns(self, text: str, words: List[Tuple[str, int, int]]) -> List[Dict]:
        """Check for verbs that require gerund (-ing) forms after them."""
        errors = []
        
        # Verbs that take gerund (verb + -ing)
        gerund_verbs = {'prefer', 'prefers', 'preferred', 'enjoy', 'enjoys', 'enjoyed',
                        'like', 'likes', 'liked', 'love', 'loves', 'loved',
                        'hate', 'hates', 'hated', 'start', 'starts', 'started',
                        'begin', 'begins', 'began', 'stop', 'stops', 'stopped',
                        'keep', 'keeps', 'kept', 'finish', 'finishes', 'finished',
                        'avoid', 'avoids', 'avoided', 'consider', 'considers', 'considered',
                        'suggest', 'suggests', 'suggested', 'recommend', 'recommends', 'recommended'}
        
        for i, (word, start, end) in enumerate(words):
            if i > 0:
                prev_word = words[i - 1][0]
                
                # If previous word is a gerund verb and current word is a base verb
                if prev_word in gerund_verbs and word in self.VERB_FORMS:
                    forms = self.VERB_FORMS[word]
                    gerund = forms[3]  # present participle (-ing form)
                    
                    errors.append({
                        'type': 'grammar',
                        'position': {'start': start, 'end': end},
                        'original': text[start:end],
                        'suggestion': gerund,
                        'explanation': f'Use "{gerund}" (gerund) after "{prev_word}".',
                        'sentenceIndex': 0,
                    })
        
        return errors
    
    def _check_third_person_verbs(self, text: str, words: List[Tuple[str, int, int]]) -> List[Dict]:
        """Check for missing -s on third person singular verbs."""
        errors = []
        
        # Third person singular subjects - EXCLUDE 'i' and 'you'
        third_person_singular = {'she', 'he', 'it'} | self.SINGULAR_SUBJECTS
        # Explicitly remove 'i' and 'you' to avoid "I reads" or "you reads" errors
        non_third_person = {'i', 'you', 'we', 'they'}
        
        # Adverbs to skip when looking for subject
        adverbs_to_skip = {'already', 'just', 'always', 'never', 'really', 'often', 
                          'usually', 'sometimes', 'also', 'only', 'even', 'still'}
        
        # Conjunctions that continue the subject
        conjunctions = {'and', 'or', 'but'}
        
        # Skip these verbs as they're handled elsewhere or are correct as-is
        skip_verbs = {'be', 'is', 'are', 'was', 'were', 'have', 'has', 'had',
                      'do', 'does', 'did', 'can', 'could', 'will', 'would',
                      'shall', 'should', 'may', 'might', 'must'}
        
        # Find the sentence subject (first third person singular word)
        sentence_subject = None
        for word, _, _ in words:
            if word in third_person_singular and word not in non_third_person:
                sentence_subject = word
                break
        
        for i, (word, start, end) in enumerate(words):
            if i > 0:
                prev_word = words[i - 1][0]
                
                # ADVERB SKIPPER: If prev_word is an adverb, look one more back
                actual_subject = prev_word
                if prev_word in adverbs_to_skip and i > 1:
                    actual_subject = words[i - 2][0]
                
                # Check if word is a base verb
                if word in self.VERB_FORMS and word not in skip_verbs:
                    should_conjugate = False
                    subject = None
                    
                    # FIX: Don't conjugate if subject is 'i' or 'you'
                    if actual_subject in non_third_person:
                        continue
                    
                    # Check if actual subject is third person singular subject
                    if actual_subject in third_person_singular:
                        should_conjugate = True
                        subject = actual_subject
                    # Check if previous word is conjunction and sentence has 3rd person subject
                    elif prev_word in conjunctions and sentence_subject:
                        # BUT: First check if there's a non-third-person subject before the conjunction
                        # This prevents "I sit and reads" from triggering
                        found_non_third = False
                        for j in range(i - 2, -1, -1):
                            check_word = words[j][0]
                            if check_word in non_third_person:
                                found_non_third = True
                                break
                            elif check_word in third_person_singular:
                                break
                        
                        if not found_non_third:
                            should_conjugate = True  
                            subject = sentence_subject
                    # Check if word before conjunction is a verb (parallel structure)
                    elif prev_word in conjunctions:
                        # Look back to see if we're in a "she verbs and verb" pattern
                        # ABORT if we find I/you/we/they first
                        for j in range(i - 2, -1, -1):
                            check_word = words[j][0]
                            if check_word in non_third_person:
                                # Subject is I/you/we/they - do NOT suggest third-person form
                                should_conjugate = False
                                break
                            elif check_word in third_person_singular and check_word not in non_third_person:
                                should_conjugate = True
                                subject = check_word
                                break
                            elif check_word in skip_verbs:
                                break
                    
                    if should_conjugate:
                        # Skip 'say' if followed by object pronoun (handled by _check_say_to_tell)
                        if word == 'say':
                            idx = i + 1
                            if idx < len(words):
                                next_word = words[idx][0]
                                # Check if next word is object pronoun
                                if next_word in {'me', 'us', 'him', 'them', 'her'}:
                                    continue

                        forms = self.VERB_FORMS[word]
                        third_person_form = forms[2]  # present 3rd person singular
                        
                        # Only suggest if it's different from current word
                        if third_person_form != word:
                            errors.append({
                                'type': 'grammar',
                                'position': {'start': start, 'end': end},
                                'original': text[start:end],
                                'suggestion': third_person_form,
                                'explanation': f'Use "{third_person_form}" with third-person singular subject.',
                                'sentenceIndex': 0,
                            })
        
        return errors
    
    def _check_plural_nouns(self, text: str, words: List[Tuple[str, int, int]]) -> List[Dict]:
        """Check for nouns that should be plural after certain patterns."""
        errors = []
        
        # Singular nouns that often should be plural in context
        countable_nouns = {
            'book': 'books', 'movie': 'movies', 'song': 'songs', 'game': 'games',
            'car': 'cars', 'house': 'houses', 'dog': 'dogs', 'cat': 'cats',
            'friend': 'friends', 'student': 'students', 'teacher': 'teachers',
            'child': 'children', 'person': 'people', 'man': 'men', 'woman': 'women',
            'day': 'days', 'year': 'years', 'hour': 'hours', 'minute': 'minutes',
            'thing': 'things', 'place': 'places', 'idea': 'ideas', 'problem': 'problems',
            'question': 'questions', 'answer': 'answers', 'story': 'stories',
            'picture': 'pictures', 'photo': 'photos', 'video': 'videos',
            'computer': 'computers', 'phone': 'phones', 'word': 'words',
            'vegetable': 'vegetables', 'fruit': 'fruits', 'animal': 'animals',
            'flower': 'flowers', 'tree': 'trees', 'city': 'cities', 'country': 'countries',
        }
        
        # Patterns that suggest plural is needed
        plural_triggers = {'reading', 'watching', 'playing', 'buying', 'selling',
                           'making', 'taking', 'writing', 'many', 'several', 'some',
                           'few', 'all', 'these', 'those', 'various', 'different',
                           'multiple', 'numerous'}
        
        for i, (word, start, end) in enumerate(words):
            if word in countable_nouns:
                plural = countable_nouns[word]
                
                # Check previous word for plural triggers
                prev_word = words[i - 1][0] if i > 0 else ""
                prev_prev_word = words[i - 2][0] if i > 1 else ""
                
                # Check if previous word is a gerund (ends in -ing) or a known plural trigger
                is_gerund = prev_word.endswith('ing') and len(prev_word) > 4
                
                # Also check for pattern like "prefers watch movie" -> "prefers watching movies"
                # where the verb before noun will become gerund
                is_verb_after_gerund_verb = (prev_word in self.VERB_FORMS and 
                                             prev_prev_word in {'prefer', 'prefers', 'preferred', 
                                                                'enjoy', 'enjoys', 'enjoyed',
                                                                'like', 'likes', 'liked',
                                                                'love', 'loves', 'loved',
                                                                'hate', 'hates', 'hated'})
                
                if prev_word in plural_triggers or is_gerund or is_verb_after_gerund_verb:
                    errors.append({
                        'type': 'grammar',
                        'position': {'start': start, 'end': end},
                        'original': text[start:end],
                        'suggestion': plural,
                        'explanation': f'Use plural "{plural}" in this context.',
                        'sentenceIndex': 0,
                    })
        
        return errors
    
    def _check_past_tense_indicator_after_verb(self, text: str, words: List[Tuple[str, int, int]]) -> List[Dict]:
        """
        Check for past-tense indicators after verbs and convert to past tense.
        Example: "they win the competition last week" -> "they won the competition last week"
        """
        errors = []
        
        # Past tense indicator phrases (multi-word and single-word)
        past_indicators_multi = [
            'last week', 'last month', 'last year', 'last night', 'last time',
            'last summer', 'last winter', 'last spring', 'last fall',
            'the other day', 'a few days ago', 'a week ago', 'a month ago',
            'a year ago', 'years ago', 'months ago', 'weeks ago', 'days ago',
            'hours ago', 'minutes ago', 'in the past', 'back then',
            'when i was', 'when we were', 'when they were',
        ]
        
        past_indicators_single = ['ago', 'yesterday']
        
        text_lower = text.lower()
        
        # Check for multi-word indicators
        for indicator in past_indicators_multi:
            if indicator in text_lower:
                indicator_pos = text_lower.find(indicator)
                
                # Look for verbs BEFORE this indicator
                for i, (word, start, end) in enumerate(words):
                    # Only check words before the indicator
                    if start >= indicator_pos:
                        break
                    
                    # Check if this word is a base form verb that should be past
                    if word in self.VERB_FORMS:
                        forms = self.VERB_FORMS[word]
                        past_form = forms[0]  # past tense
                        
                        # Only flag if current word is NOT already past tense
                        if word != past_form and word == word:  # base form
                            # Check that we're not already past tense
                            # and that the word comes after a subject (not at start)
                            if i > 0:
                                errors.append({
                                    'type': 'grammar',
                                    'position': {'start': start, 'end': end},
                                    'original': text[start:end],
                                    'suggestion': past_form,
                                    'explanation': f'Use past tense "{past_form}" because of "{indicator}".',
                                    'sentenceIndex': 0,
                                })
        
        # Check for single-word indicators like "yesterday" at end or "ago"
        for i, (word, start, end) in enumerate(words):
            if word in past_indicators_single:
                # Look backwards for verbs in base form
                for j in range(i - 1, -1, -1):
                    prev_word, prev_start, prev_end = words[j]
                    
                    if prev_word in self.VERB_FORMS:
                        forms = self.VERB_FORMS[prev_word]
                        past_form = forms[0]
                        
                        if prev_word != past_form:
                            errors.append({
                                'type': 'grammar',
                                'position': {'start': prev_start, 'end': prev_end},
                                'original': text[prev_start:prev_end],
                                'suggestion': past_form,
                                'explanation': f'Use past tense "{past_form}" because of "{word}".',
                                'sentenceIndex': 0,
                            })
                    # Only check up to 5 words back
                    if i - j > 5:
                        break
        
        return errors
    
    def _check_incorrect_regularized_past(self, text: str, words: List[Tuple[str, int, int]]) -> List[Dict]:
        """
        Check for incorrect regularized past tense of irregular verbs.
        Example: "buyed" -> "bought", "goed" -> "went", "taked" -> "took"
        
        Common mistake for ESL learners who apply regular -ed rule to irregular verbs.
        """
        errors = []
        
        # Build a mapping of incorrect forms to correct forms
        # Pattern: base + "ed" or base + "d" (for verbs ending in e)
        incorrect_to_correct = {}
        
        for base, forms in self.VERB_FORMS.items():
            past_form = forms[0]
            
            # Skip if the verb is regular (past already ends in -ed)
            if past_form == base + 'ed' or past_form == base + 'd':
                continue
            
            # Generate incorrect forms
            # buyed, goed, taked, comed, etc.
            if base.endswith('e'):
                incorrect = base + 'd'  # take -> taked
            else:
                incorrect = base + 'ed'  # buy -> buyed, go -> goed
            
            # Also handle doubling consonant (runed instead of ran)
            if len(base) > 2 and base[-1] in 'bdgmnprt' and base[-2] in 'aeiou':
                incorrect_doubled = base + base[-1] + 'ed'  # run -> runned
                incorrect_to_correct[incorrect_doubled] = past_form
            
            incorrect_to_correct[incorrect] = past_form
        
        # Check each word
        for word, start, end in words:
            if word in incorrect_to_correct:
                correct = incorrect_to_correct[word]
                
                errors.append({
                    'type': 'grammar',
                    'position': {'start': start, 'end': end},
                    'original': text[start:end],
                    'suggestion': correct,
                    'explanation': f'Irregular verb: use "{correct}" instead of "{word}".',
                    'sentenceIndex': 0,
                })
        
        return errors
    
    def _check_pronoun_capitalization(self, text: str, words: List[Tuple[str, int, int]]) -> List[Dict]:
        """
        Check for lowercase 'i' pronoun that should be capitalized.
        Example: "i went" -> "I went"
        """
        errors = []
        
        for word, start, end in words:
            if word == 'i':
                # Check it's a standalone 'i', not part of another word
                # Already handled by tokenization, but double check
                errors.append({
                    'type': 'grammar',
                    'position': {'start': start, 'end': end},
                    'original': text[start:end],
                    'suggestion': 'I',
                    'explanation': 'The pronoun "I" should always be capitalized.',
                    'sentenceIndex': 0,
                })
        
        return errors
    
    def _check_double_comparatives(self, text: str, words: List[Tuple[str, int, int]]) -> List[Dict]:
        """
        Check for redundant double comparatives.
        Example: "more better" -> "better", "most best" -> "best"
        """
        errors = []
        
        # Patterns: more/most + already comparative/superlative
        double_comparatives = {
            'more better': 'better',
            'more worse': 'worse',
            'more faster': 'faster',
            'more slower': 'slower',
            'more louder': 'louder',
            'more quieter': 'quieter',
            'more bigger': 'bigger',
            'more smaller': 'smaller',
            'more easier': 'easier',
            'more harder': 'harder',
            'most best': 'best',
            'most worst': 'worst',
            'most fastest': 'fastest',
            'most slowest': 'slowest',
            'most loudest': 'loudest',
            'most biggest': 'biggest',
            'most smallest': 'smallest',
            'most easiest': 'easiest',
        }
        
        text_lower = text.lower()
        
        for incorrect, correct in double_comparatives.items():
            if incorrect in text_lower:
                idx = text_lower.find(incorrect)
                end_idx = idx + len(incorrect)
                
                errors.append({
                    'type': 'grammar',
                    'position': {'start': idx, 'end': end_idx},
                    'original': text[idx:end_idx],
                    'suggestion': correct,
                    'explanation': f'Double comparative: use "{correct}" instead of "{incorrect}".',
                    'sentenceIndex': 0,
                })
        
        return errors
    
    def _check_infinitive_patterns(self, text: str, words: List[Tuple[str, int, int]]) -> List[Dict]:
        """
        Check for missing 'to' after verbs that require infinitives.
        Example: "forget bring" -> "forget to bring"
        """
        errors = []
        
        # Verbs that require 'to' + infinitive
        infinitive_verbs = {
            'want', 'wants', 'wanted',
            'need', 'needs', 'needed',
            'decide', 'decides', 'decided',
            'forget', 'forgets', 'forgot', 'forgotten',
            'hope', 'hopes', 'hoped',
            'plan', 'plans', 'planned',
            'learn', 'learns', 'learned', 'learnt',
            'agree', 'agrees', 'agreed',
            'promise', 'promises', 'promised',
            'refuse', 'refuses', 'refused',
            'expect', 'expects', 'expected',
            'prepare', 'prepares', 'prepared',
            'try', 'tries', 'tried',
            'manage', 'manages', 'managed',
            'afford', 'affords', 'afforded',
            'choose', 'chooses', 'chose', 'chosen',
            'offer', 'offers', 'offered',
        }
        
        for i, (word, start, end) in enumerate(words):
            if word in infinitive_verbs:
                # Check if next word exists and is NOT 'to'
                if i + 1 < len(words):
                    next_word, next_start, next_end = words[i + 1]
                    
                    # If next word is a base verb (not 'to' and in VERB_FORMS)
                    if next_word != 'to' and next_word in self.VERB_FORMS:
                        # Suggest adding 'to'
                        errors.append({
                            'type': 'grammar',
                            'position': {'start': next_start, 'end': next_end},
                            'original': text[next_start:next_end],
                            'suggestion': 'to ' + text[next_start:next_end],
                            'explanation': f'Use infinitive form: "{word} to {next_word}".',
                            'sentenceIndex': 0,
                        })
        
        return errors
    
    def _check_articles(self, text: str, words: List[Tuple[str, int, int]]) -> List[Dict]:
        """
        Check for incorrect article usage (a vs an).
        Example: "a apple" -> "an apple", "an car" -> "a car"
        """
        errors = []
        
        # Words that start with vowel sounds but consonant letters
        vowel_sound_consonants = {'hour', 'honest', 'honor', 'honour', 'heir'}
        
        # Words that start with consonant sounds but vowel letters
        consonant_sound_vowels = {'university', 'uniform', 'unique', 'unit', 'united',
                                   'european', 'one', 'once', 'useful', 'user'}
        
        for i, (word, start, end) in enumerate(words):
            if word in ('a', 'an'):
                # Check next word
                if i + 1 < len(words):
                    next_word, next_start, next_end = words[i + 1]
                    first_letter = next_word[0] if next_word else ''
                    
                    should_be_an = (first_letter in 'aeiou' or 
                                   next_word.lower() in vowel_sound_consonants)
                    should_be_a = (first_letter not in 'aeiou' or 
                                  next_word.lower() in consonant_sound_vowels)
                    
                    # Check for special cases
                    if next_word.lower() in vowel_sound_consonants:
                        should_be_an = True
                        should_be_a = False
                    elif next_word.lower() in consonant_sound_vowels:
                        should_be_a = True
                        should_be_an = False
                    
                    if word == 'a' and should_be_an and not should_be_a:
                        errors.append({
                            'type': 'grammar',
                            'position': {'start': start, 'end': end},
                            'original': text[start:end],
                            'suggestion': 'an',
                            'explanation': f'Use "an" before words starting with a vowel sound.',
                            'sentenceIndex': 0,
                        })
                    elif word == 'an' and should_be_a and not should_be_an:
                        errors.append({
                            'type': 'grammar',
                            'position': {'start': start, 'end': end},
                            'original': text[start:end],
                            'suggestion': 'a',
                            'explanation': f'Use "a" before words starting with a consonant sound.',
                            'sentenceIndex': 0,
                        })
        
        return errors
    
    def _check_adverbs(self, text: str, words: List[Tuple[str, int, int]]) -> List[Dict]:
        """
        Check for adjectives used where adverbs are required.
        Example: "He runs quick" -> "He runs quickly"
        """
        errors = []
        
        # Adjective to adverb mapping
        adj_to_adv = {
            'quick': 'quickly',
            'slow': 'slowly',
            'loud': 'loudly',
            'quiet': 'quietly',
            'soft': 'softly',
            'hard': 'hard',  # Exception: hard is both adj and adv
            'fast': 'fast',  # Exception: fast is both adj and adv
            'bad': 'badly',
            'easy': 'easily',
            'careful': 'carefully',
            'careless': 'carelessly',
            'beautiful': 'beautifully',
            'nice': 'nicely',
            'clear': 'clearly',
            'safe': 'safely',
            'perfect': 'perfectly',
            'complete': 'completely',
            'immediate': 'immediately',
            'sudden': 'suddenly',
            'real': 'really',
            'extreme': 'extremely',
        }
        
        # Verbs after which we expect adverbs
        action_verbs = {
            'run', 'runs', 'ran', 'running',
            'walk', 'walks', 'walked', 'walking',
            'speak', 'speaks', 'spoke', 'speaking',
            'talk', 'talks', 'talked', 'talking',
            'move', 'moves', 'moved', 'moving',
            'work', 'works', 'worked', 'working',
            'drive', 'drives', 'drove', 'driving',
            'play', 'plays', 'played', 'playing',
            'sing', 'sings', 'sang', 'singing',
            'dance', 'dances', 'danced', 'dancing',
            'write', 'writes', 'wrote', 'writing',
            'read', 'reads', 'reading',
            'eat', 'eats', 'ate', 'eating',
            'sleep', 'sleeps', 'slept', 'sleeping',
        }
        
        for i, (word, start, end) in enumerate(words):
            if word in action_verbs:
                # Check next word
                if i + 1 < len(words):
                    next_word, next_start, next_end = words[i + 1]
                    
                    if next_word in adj_to_adv and adj_to_adv[next_word] != next_word:
                        adverb = adj_to_adv[next_word]
                        errors.append({
                            'type': 'grammar',
                            'position': {'start': next_start, 'end': next_end},
                            'original': text[next_start:next_end],
                            'suggestion': adverb,
                            'explanation': f'Use adverb "{adverb}" to modify the verb.',
                            'sentenceIndex': 0,
                        })
        
        return errors
    
    def _check_redundancy(self, text: str, words: List[Tuple[str, int, int]]) -> List[Dict]:
        """
        Check for redundant/tautological phrases.
        Example: "return back" -> "return", "repeat again" -> "repeat"
        """
        errors = []
        
        redundant_phrases = {
            'return back': 'return',
            'reply back': 'reply',
            'repeat again': 'repeat',
            'revert back': 'revert',
            'join together': 'join',
            'combine together': 'combine',
            'merge together': 'merge',
            'mix together': 'mix',
            'past history': 'history',
            'future plans': 'plans',
            'advance planning': 'planning',
            'added bonus': 'bonus',
            'free gift': 'gift',
            'new innovation': 'innovation',
            'end result': 'result',
            'final outcome': 'outcome',
            'close proximity': 'proximity',
            'exact same': 'same',
            'atm machine': 'ATM',
            'pin number': 'PIN',
            'completely empty': 'empty',
            'completely full': 'full',
            'very unique': 'unique',
        }
        
        text_lower = text.lower()
        
        for redundant, correct in redundant_phrases.items():
            if redundant in text_lower:
                idx = text_lower.find(redundant)
                end_idx = idx + len(redundant)
                
                errors.append({
                    'type': 'grammar',
                    'position': {'start': idx, 'end': end_idx},
                    'original': text[idx:end_idx],
                    'suggestion': correct,
                    'explanation': f'Redundant phrase: "{redundant}" -> "{correct}".',
                    'sentenceIndex': 0,
                })
        
        return errors
    
    def _check_prepositions(self, text: str, words: List[Tuple[str, int, int]]) -> List[Dict]:
        """
        Check for common preposition errors (especially ESL errors).
        """
        errors = []
        
        # Two-word preposition patterns (word + wrong_prep -> correct)
        preposition_errors = {
            'married with': ('married to', 'Use "married to" not "married with".'),
            'good in': ('good at', 'Use "good at" for skills.'),
            'angry on': ('angry at', 'Use "angry at" or "angry with".'),
            'different to': ('different from', 'Use "different from".'),
            'superior than': ('superior to', 'Use "superior to".'),
            'inferior than': ('inferior to', 'Use "inferior to".'),
            'consist in': ('consist of', 'Use "consist of".'),
            'die from': ('die of', 'Usually "die of" for diseases.'),
            # NEW PATTERNS
            'depend of': ('depend on', 'Use "depend on".'),
            'arrive to': ('arrive at', 'Use "arrive at" (place) or "arrive in" (city/country).'),
            'listen her': ('listen to her', 'Use "listen to" before a person.'),
            'listening her': ('listening to her', 'Use "listening to".'),
            'listen him': ('listen to him', 'Use "listen to" before a person.'),
            'listening him': ('listening to him', 'Use "listening to".'),
            'listen me': ('listen to me', 'Use "listen to" before a person.'),
            'listening me': ('listening to me', 'Use "listening to".'),
            'explain me': ('explain to me', 'Use "explain to" before a person.'),
            'describe me': ('describe to me', 'Use "describe to" before a person.'),
        }
        
        text_lower = text.lower()
        
        for wrong, (correct, explanation) in preposition_errors.items():
            if wrong in text_lower:
                idx = text_lower.find(wrong)
                end_idx = idx + len(wrong)
                
                errors.append({
                    'type': 'grammar',
                    'position': {'start': idx, 'end': end_idx},
                    'original': text[idx:end_idx],
                    'suggestion': correct,
                    'explanation': explanation,
                    'sentenceIndex': 0,
                })
        
        # Check "discuss about" (should be just "discuss")
        for i, (word, start, end) in enumerate(words):
            if word == 'discuss' and i + 1 < len(words):
                next_word, next_start, next_end = words[i + 1]
                if next_word == 'about':
                    errors.append({
                        'type': 'grammar',
                        'position': {'start': next_start, 'end': next_end},
                        'original': text[next_start:next_end],
                        'suggestion': '',
                        'explanation': '"Discuss" doesn\'t need "about" after it.',
                        'sentenceIndex': 0,
                    })
        
        # Check "lack of" when used as verb (should be just "lack")
        for i, (word, start, end) in enumerate(words):
            if word == 'lack' and i + 1 < len(words):
                next_word, next_start, next_end = words[i + 1]
                # Check if "lack" is used as verb (after subject)
                if next_word == 'of' and i > 0:
                    prev_word = words[i - 1][0]
                    # If preceded by subject pronoun, it's a verb
                    if prev_word in ('i', 'we', 'they', 'you', 'he', 'she', 'it'):
                        errors.append({
                            'type': 'grammar',
                            'position': {'start': next_start, 'end': next_end},
                            'original': text[next_start:next_end],
                            'suggestion': '',
                            'explanation': 'As a verb, "lack" doesn\'t need "of".',
                            'sentenceIndex': 0,
                        })
        
        # Check "go + noun" pattern
        # Fixes "go library" -> "go to the library" vs "go school" -> "go to school"
        
        # Places that typically take NO article (Zero Article)
        zero_article_places = {'home', 'work', 'school', 'bed', 'church', 'college', 'university', 'jail', 'prison', 'camp', 'class'}
        
        # Places that typically take "THE"
        definite_article_places = {'library', 'mall', 'park', 'cinema', 'theater', 'gym', 'station', 'airport', 'doctor', 'dentist', 'bank', 'store', 'shop', 'market', 'office', 'beach', 'zoo', 'museum'}
        
        go_exceptions = {'to', 'into', 'in', 'out', 'up', 'down', 'away', 'back', 'on', 'off', 'over', 'through', 'round', 'under', 'ahead', 'there', 'here', 'now', 'first', 'fast', 'slow'}
        
        for i, (word, start, end) in enumerate(words):
            if word in ('go', 'goes', 'went', 'going') and i + 1 < len(words):
                next_word, next_start, next_end = words[i + 1]
                
                if next_word not in go_exceptions:
                    # Case 1: Needs "to" only (e.g., "go school" -> "go to school")
                    if next_word in zero_article_places:
                        errors.append({
                            'type': 'grammar',
                            'position': {'start': next_start, 'end': next_end},
                            'original': text[next_start:next_end],
                            'suggestion': 'to ' + text[next_start:next_end],
                            'explanation': f'Use "to" before "{next_word}".',
                            'sentenceIndex': 0,
                        })
                    # Case 2: Needs "to the" (e.g., "go library" -> "go to the library")
                    elif next_word in definite_article_places or (next_word.endswith('s') and next_word not in zero_article_places):
                        errors.append({
                            'type': 'grammar',
                            'position': {'start': next_start, 'end': next_end},
                            'original': text[next_start:next_end],
                            'suggestion': 'to the ' + text[next_start:next_end],
                            'explanation': f'Use "to the" before "{next_word}".',
                            'sentenceIndex': 0,
                        })
        
        return errors
    
    def _check_confused_words(self, text: str, words: List[Tuple[str, int, int]]) -> List[Dict]:
        """
        Check for commonly confused words based on context.
        your/you're, their/there/they're, its/it's, loose/lose
        """
        errors = []
        
        for i, (word, start, end) in enumerate(words):
            # Check your/you're
            if word == 'your' and i + 1 < len(words):
                next_word = words[i + 1][0]
                # If followed by a verb ending in -ing, should be "you're"
                if next_word.endswith('ing') and len(next_word) > 4:
                    errors.append({
                        'type': 'grammar',
                        'position': {'start': start, 'end': end},
                        'original': text[start:end],
                        'suggestion': "you're",
                        'explanation': '"You\'re" (you are) + verb-ing, not "your".',
                        'sentenceIndex': 0,
                    })
                # "your welcome" -> "you're welcome"
                elif next_word == 'welcome':
                    errors.append({
                        'type': 'grammar',
                        'position': {'start': start, 'end': end},
                        'original': text[start:end],
                        'suggestion': "you're",
                        'explanation': '"You\'re welcome" not "your welcome".',
                        'sentenceIndex': 0,
                    })
            
            # Check their/there
            if word == 'their' and i + 1 < len(words):
                next_word = words[i + 1][0]
                # "their is/are/was/were" -> "there is/are/was/were"
                if next_word in ('is', 'are', 'was', 'were'):
                    errors.append({
                        'type': 'grammar',
                        'position': {'start': start, 'end': end},
                        'original': text[start:end],
                        'suggestion': 'there',
                        'explanation': '"There" + be verb, not "their".',
                        'sentenceIndex': 0,
                    })
            
            # Check loose/lose
            if word == 'loose':
                # Check context for verb usage
                if i > 0:
                    prev_word = words[i - 1][0]
                    # After modal verbs, should be "lose"
                    if prev_word in ('will', 'would', 'could', 'might', 'may', 'can', 
                                    'should', 'did', 'do', 'does', "don't", "didn't",
                                    'to', 'not', "won't", "wouldn't", "couldn't"):
                        errors.append({
                            'type': 'grammar',
                            'position': {'start': start, 'end': end},
                            'original': text[start:end],
                            'suggestion': 'lose',
                            'explanation': '"Lose" (verb) not "loose" (adjective).',
                            'sentenceIndex': 0,
                        })
            
            # Check its/it's
            if word == "its" and i + 1 < len(words):
                next_word = words[i + 1][0]
                # "its" + adjective is often wrong (should be "it's")
                if next_word in ('a', 'the', 'very', 'really', 'so', 'too', 'not',
                                'going', 'been', 'being'):
                    errors.append({
                        'type': 'grammar',
                        'position': {'start': start, 'end': end},
                        'original': text[start:end],
                        'suggestion': "it's",
                        'explanation': '"It\'s" (it is) may be needed here, not "its".',
                        'sentenceIndex': 0,
                    })
        
        return errors
    
    def _check_quantifiers(self, text: str, words: List[Tuple[str, int, int]]) -> List[Dict]:
        """
        Check for incorrect quantifier usage.
        Example: "no enough" -> "not enough"
        """
        errors = []
        
        # Check for "no enough" pattern
        text_lower = text.lower()
        if 'no enough' in text_lower:
            idx = text_lower.find('no enough')
            # Just flag "no" for replacement with "not"
            errors.append({
                'type': 'grammar',
                'position': {'start': idx, 'end': idx + 2},
                'original': text[idx:idx + 2],
                'suggestion': 'not',
                'explanation': 'Use "not enough" instead of "no enough".',
                'sentenceIndex': 0,
            })
        
        return errors
    
    def _check_prepositions_context(self, text: str, words: List[Tuple[str, int, int]]) -> List[Dict]:
        """
        Check for preposition errors that require context analysis.
        - "bring ... at home" -> "bring ... from home" or "leave ... at home"
        - "angry to me" -> "angry with me"
        """
        errors = []
        
        text_lower = text.lower()
        
        # Check "angry to" pattern
        if 'angry to' in text_lower:
            idx = text_lower.find('angry to')
            # Flag "to" for replacement with "with"
            to_idx = idx + len('angry ')
            errors.append({
                'type': 'grammar',
                'position': {'start': to_idx, 'end': to_idx + 2},
                'original': text[to_idx:to_idx + 2],
                'suggestion': 'with',
                'explanation': 'Use "angry with" or "angry at", not "angry to".',
                'sentenceIndex': 0,
            })
        
        # Check "bring ... at home" pattern
        for i, (word, start, end) in enumerate(words):
            if word == 'bring':
                # Look ahead for "at home"
                for j in range(i + 1, min(i + 6, len(words))):
                    if j + 1 < len(words):
                        if words[j][0] == 'at' and words[j + 1][0] == 'home':
                            at_start = words[j][1]
                            at_end = words[j][2]
                            errors.append({
                                'type': 'grammar',
                                'position': {'start': at_start, 'end': at_end},
                                'original': text[at_start:at_end],
                                'suggestion': 'from',
                                'explanation': 'Use "bring from home" (origin), not "bring at home".',
                                'sentenceIndex': 0,
                            })
                            break
        
        # Check "interested for" pattern (should be "interested in")
        if 'interested for' in text_lower:
            idx = text_lower.find('interested for')
            for_idx = idx + len('interested ')
            errors.append({
                'type': 'grammar',
                'position': {'start': for_idx, 'end': for_idx + 3},
                'original': text[for_idx:for_idx + 3],
                'suggestion': 'in',
                'explanation': 'Use "interested in", not "interested for".',
                'sentenceIndex': 0,
            })
        
        return errors
    
    def _check_possessives_context(self, text: str, words: List[Tuple[str, int, int]]) -> List[Dict]:
        """
        Check for missing apostrophe-s with family and relationship words.
        Example: "my brother car" -> "my brother's car"
        """
        errors = []
        
        # Trigger words: family and relationship terms
        family_triggers = {
            'mother', 'father', 'brother', 'sister', 'aunt', 'uncle',
            'cousin', 'neighbor', 'friend', 'boss', 'teacher', 'student',
            'son', 'daughter', 'husband', 'wife', 'parent', 'grandma',
            'grandpa', 'grandmother', 'grandfather', 'colleague', 'partner'
        }
        
        # Common nouns that often follow possessives
        possessive_objects = {
            'car', 'house', 'phone', 'book', 'bag', 'room', 'desk', 'computer',
            'job', 'work', 'office', 'idea', 'opinion', 'decision', 'advice',
            'name', 'birthday', 'wedding', 'home', 'apartment', 'money',
            'wallet', 'keys', 'friend', 'problem', 'fault', 'mistake'
        }
        
        for i, (word, start, end) in enumerate(words):
            word_lower = word.lower()
            
            # Check if this is a family/relation word
            if word_lower in family_triggers and not word_lower.endswith("'s"):
                # Check if next word is a noun (not a verb or preposition)
                if i + 1 < len(words):
                    next_word, next_start, next_end = words[i + 1]
                    next_lower = next_word.lower()
                    
                    # Skip if next word is a verb or preposition
                    skip_words = {'is', 'are', 'was', 'were', 'has', 'have', 'had',
                                 'will', 'would', 'can', 'could', 'should', 'may',
                                 'said', 'says', 'told', 'tells', 'went', 'goes',
                                 'in', 'on', 'at', 'to', 'for', 'with', 'and', 'or'}
                    
                    if next_lower not in skip_words:
                        # Check if next word is in common possessive objects
                        # OR is a noun-like word (not ending in common verb suffixes)
                        if next_lower in possessive_objects:
                            suggestion = word + "'s"
                            errors.append({
                                'type': 'grammar',
                                'position': {'start': start, 'end': end},
                                'original': text[start:end],
                                'suggestion': suggestion,
                                'explanation': f'Use possessive "{suggestion}" before a noun.',
                                'sentenceIndex': 0,
                            })
        
        return errors


# Global instance
_grammar_rules_checker = None


def get_grammar_rules_checker() -> GrammarRulesChecker:
    """Get the global grammar rules checker instance."""
    global _grammar_rules_checker
    if _grammar_rules_checker is None:
        _grammar_rules_checker = GrammarRulesChecker()
    return _grammar_rules_checker

