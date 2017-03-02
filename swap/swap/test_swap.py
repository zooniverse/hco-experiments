from swap import SWAP

def test_subject_update_perfect_classifier():

  swap = SWAP(p0=2e-4, epsilon=1.0)

  cl = {
          'user_name'  : 'user_1',
          'subject_id' : 'subject_1',
          'annotation' : '1',
          'gold_label' : '1'
       }

  swap.processOneClassification(cl)
  print(swap.getSubjectData())

  assert swap.getSubjectData()['subject_1']['current_max_prob'] == 1

  cl = {
          'user_name'  : 'user_1',
          'subject_id' : 'subject_2',
          'annotation' : '0',
          'gold_label' : '0'
       }

  swap.processOneClassification(cl)
  print(swap.getSubjectData())

  assert swap.getSubjectData()['subject_2']['current_max_prob'] == 0

def test_subject_update_obtuse_classifier():

  swap = SWAP(p0=2e-4, epsilon=0.0)

  cl = {
          'user_name'  : 'user_1',
          'subject_id' : 'subject_1',
          'annotation' : '0',
          'gold_label' : '1'
       }

  swap.processOneClassification(cl)
  print(swap.getSubjectData())

  assert swap.getSubjectData()['subject_1']['current_max_prob'] == 1

  cl = {
          'user_name'  : 'user_1',
          'subject_id' : 'subject_2',
          'annotation' : '1',
          'gold_label' : '0'
       }

  swap.processOneClassification(cl)
  print(swap.getSubjectData())

  assert swap.getSubjectData()['subject_2']['current_max_prob'] == 0

def my_volunteer_update(user,annotation,gold_label):
    user[gold_label]['tot'] += 1
    if gold_label == annotation:
        user[gold_label]['correct'] += 1
    user[gold_label]['p'] = user[gold_label]['correct'] / float(user[gold_label]['tot'])
    return user

def my_subject_update(p0,user,annotation):
  
  if annotation == '1':
    S = p0*user['1']['p'] / (p0*user['1']['p'] + (1-user['0']['p'])*(1-p0))
  elif annotation == '0':
    S = p0*(1-user['1']['p']) / (p0*(1-user['1']['p']) + (user['0']['p'])*(1-p0))
  return S

def test_subject_update_apply_one_correct_classification():

  p0 = 0.2
  epsilon = 0.5
  annotation = '1'
  gold_label = '1'
  
  swap = SWAP(p0=p0, epsilon=epsilon)

  cl = {
          'user_name'  : 'user_1',
          'subject_id' : 'subject_1',
          'annotation' : annotation,
          'gold_label' : gold_label
       }
       
  user = {
           '1':{'tot':0,'correct':0, 'p':epsilon},
           '0':{'tot':0,'correct':0, 'p':epsilon}
         }

  swap.processOneClassification(cl)
  user = my_volunteer_update(user,annotation,gold_label)
  assert swap.getSubjectData()['subject_1']['current_max_prob'] == my_subject_update(p0,user,annotation)

def test_subject_update_apply_one_incorrect_classification():

  p0 = 0.2
  epsilon = 0.5
  annotation = '0'
  gold_label = '1'
  
  swap = SWAP(p0=p0, epsilon=epsilon)

  cl = {
          'user_name'  : 'user_1',
          'subject_id' : 'subject_1',
          'annotation' : annotation,
          'gold_label' : gold_label
       }
       
  user = {
           '1':{'tot':0,'correct':0, 'p':epsilon},
           '0':{'tot':0,'correct':0, 'p':epsilon}
         }

  swap.processOneClassification(cl)
  user = my_volunteer_update(user,annotation,gold_label)
  assert swap.getSubjectData()['subject_1']['current_max_prob'] == my_subject_update(p0,user,annotation)

def main():

  test_subject_update_perfect_classifier()
  test_subject_update_obtuse_classifier()
  
  test_subject_update_apply_one_correct_classification()
  test_subject_update_apply_one_incorrect_classification()

if __name__ == "__main__":
    main()
