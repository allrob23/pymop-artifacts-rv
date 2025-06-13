import itertools
from pythonmop.logicplugin import javamop
from pytest import raises

def remove_whitespace(input_str):
   return input_str.replace(" ", "").replace("\t", "").replace("\n", "")

class TestJavaMop:
   def test_invoke_logic_plugin_ere(self):
      input_string = '''
      <mop>
         <Client>Web</Client>
         <Events>a b</Events>
         <Property>
            <Logic>ere</Logic>
            <Formula>(a b)* ~(b ~(a b))</Formula>
         </Property>
         <Categories>fail match</Categories>
      </mop>
      '''

      expected_output = remove_whitespace('''
      <mop>
         <Client>Web</Client>
         <Events>a b</Events>
         <Property>
            <Logic>fsm</Logic>
            <Formula>
               s0 [
                  a -&gt; s1
                  b -&gt; s7
               ]
               s1 [
                  a -&gt; s2
                  b -&gt; s3
               ]
               s2 [
                  a -&gt; s2
                  b -&gt; s2
               ]
               s3 [
                  a -&gt; s1
                  b -&gt; s4
               ]
               s4 [
                  a -&gt; s5
                  b -&gt; s2
               ]
               s5 [
                  a -&gt; s2
                  b -&gt; s6
               ]
               s6 [
                  a -&gt; s2
                  b -&gt; s2
               ]
               s7 [
                  a -&gt; s8
               ]
               s8 [
                  b -&gt; s9
               ]
               s9 []
               alias match = s0 s1 s2 s3 s4 s5 s6 s9 
            </Formula>
         </Property>
         <Categories>fail match</Categories>
      </mop>
      ''')

      result = remove_whitespace(javamop.invokeLogicPlugin("ere", input_string))

      assert expected_output == result

   def test_invoke_logic_plugin_ltl(self):
      input_string = '''
      <mop>
         <Client>Web</Client>
         <Events>request acquire</Events>
         <Property>
            <Logic>ltl</Logic>
            <Formula>[](acquire => (*) request)</Formula>
         </Property>
         <Categories>violation</Categories>
      </mop>
      '''

      # This is the expected output, but we'll be constructing it from permutations of the
      # states because the order of the states is non-deterministic
      '''
      <mop>
         <Client>Web</Client>
         <Events>request acquire</Events>
         <Property>
            <Logic>fsm</Logic>
            <Formula>
               s0[
                  acquire -&gt; violation
                  request -&gt; s1
                  default s2
               ]
               s1[
                  acquire -&gt; s2
                  request -&gt; s1
                  default s2
               ]
               s2[
                  acquire -&gt; violation
                  request -&gt; s1
                  default s2
               ]
               violation[]
            </Formula>
         </Property>
         <Categories>violation</Categories>
      </mop>
      '''
      s0_components = ['request -&gt; s1', 'acquire -&gt; violation', 'default s2']
      s1_components = ['request -&gt; s1', 'acquire -&gt; s2', 'default s2']
      s2_components = ['request -&gt; s1', 'acquire -&gt; violation', 'default s2']
      violation_components = ['']
      state_order = ['s0', 's1', 's2', 'violation']

      state_permutations = list(itertools.permutations(state_order))
      s0_permutations = list(itertools.permutations(s0_components))
      s1_permutations = list(itertools.permutations(s1_components))
      s2_permutations = list(itertools.permutations(s2_components))
      violation_permutations = list(itertools.permutations(violation_components))

      all_permutations = []
      expected_permutations = []

      for state_perm in state_permutations:
         for s0_perm in s0_permutations:
            for s1_perm in s1_permutations:
               for s2_perm in s2_permutations:
                  for violation_perm in violation_permutations:
                     perm_dict = {
                        's0': s0_perm,
                        's1': s1_perm,
                        's2': s2_perm,
                        'violation': violation_perm
                     }

                     all_permutations.append(
                        {
                           state: perm_dict[state] for state in state_perm
                        }
                     )

      for perm in all_permutations:
         states_order = list(perm.keys())

         expected_permutations.append(remove_whitespace(f'''   
         <mop>
            <Client>Web</Client>
            <Events>request acquire</Events>
            <Property>
               <Logic>fsm</Logic>
               <Formula>
                  {states_order[0]}[
                     {' '.join(perm[states_order[0]])}
                  ]
                  {states_order[1]}[
                     {' '.join(perm[states_order[1]])}
                  ]
                  {states_order[2]}[
                     {' '.join(perm[states_order[2]])}
                  ]
                  {states_order[3]}[
                     {' '.join(perm[states_order[3]])}
                  ]
               </Formula>
            </Property>
            <Categories>violation</Categories>
         </mop>
         '''))

      result = remove_whitespace(javamop.invokeLogicPlugin("ltl", input_string))

      assert result in expected_permutations

   def test_invalid_logic(self):
      invalid_logic = 'invalid_logic_type'
      input_string = '<some_xml></some_xml>'

      with raises(ValueError):
         javamop.invokeLogicPlugin(invalid_logic, input_string)

