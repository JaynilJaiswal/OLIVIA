from models.user import db, User,User_location ,User_command_history, User_music, User_contacts_email, User_contacts_whatsapp
from similarity.jarowinkler import JaroWinkler

jarowinkler = JaroWinkler()

def get_contact_email_info(db,User_contacts_email,user_base_id, person_name):
    userId_contacts = list(db.query(User_contacts_email).filter_by(user_base_id=user_base_id))

    if len(userId_contacts) == 0:
        return [-1,-1,-1]
        
    userId_contacts_name_email = [[e.contact_fname + " " +e.contact_lname, e.contact_email] for e in userId_contacts]

    name_similarity = [[0,0,0]]*len(userId_contacts_name_email)

    for i,el in enumerate(userId_contacts_name_email):
        name_similarity[i] = [jarowinkler.similarity(person_name.lower(), el[0].strip().lower()),el[0],el[1]]

    best_matched_contact = sorted(name_similarity, key=lambda x: x[0])[-1]

    if best_matched_contact[0] >= 0.8:
        return best_matched_contact
    else:
        return [0,0,0]

def get_contact_whatsapp_info(db,User_contacts_whatsapp,user_base_id, person_name):

    userId_contacts = list(db.query(User_contacts_whatsapp).filter_by(user_base_id=user_base_id))

    if len(userId_contacts) == 0:
        return [-1,-1,-1]

    userId_contacts_name_whatsapp = [[e.contact_name , e.contact_id] for e in userId_contacts]

    name_similarity = [[0,0,0]]*len(userId_contacts_name_whatsapp)

    for i,el in enumerate(userId_contacts_name_whatsapp):
        name_similarity[i] = [jarowinkler.similarity(person_name.lower(), el[0].strip().lower()),el[0],el[1]]

    best_matched_contact = sorted(name_similarity, key=lambda x: x[0])[-1]

    if best_matched_contact[0] >= 0.8:
        return best_matched_contact
    else:
        return [0,0,0]
    return
