"""
This file defines actions, i.e. functions the URLs are mapped into
The @action(path) decorator exposed the function at URL:

    http://127.0.0.1:8000/{app_name}/{path}

If app_name == '_default' then simply

    http://127.0.0.1:8000/{path}

If path == 'index' it can be omitted:

    http://127.0.0.1:8000/

The path follows the bottlepy syntax.

@action.uses('generic.html')  indicates that the action uses the generic.html template
@action.uses(session)         indicates that the action uses the session
@action.uses(db)              indicates that the action uses the db
@action.uses(T)               indicates that the action uses the i18n & pluralization
@action.uses(auth.user)       indicates that the action requires a logged in user
@action.uses(auth)            indicates that the action requires the auth object

session, db, T, auth, and tempates are examples of Fixtures.
Warning: Fixtures MUST be declared with @action.uses({fixtures}) else your app will result in undefined behavior
"""

from py4web import action, request, abort, redirect, URL
from yatl.helpers import A
from .common import db, session, T, cache, auth, logger, authenticated, unauthenticated, flash
from py4web.utils.url_signer import URLSigner
from .models import get_user_email, get_user
from py4web.utils.form import Form, FormStyleBulma
import yatl 
import json
from .settings import APP_FOLDER
import os
BREED_JSON_FILE = os.path.join(APP_FOLDER, "data", "breeds.json")

url_signer = URLSigner(session)


# ============ INDEX.JS ========================= 
@action('index', method=["GET", "POST"])
@action.uses(db, auth, auth.user, 'index.html')
def index():
    returning_user = db(db.dbuser.auth == get_user() ).select().first()
    if returning_user is None: # user has no entry
        db.dbuser.insert(
            auth = get_user(),
            first_name = auth.current_user.get('first_name'),
            last_name = auth.current_user.get('last_name'),
            user_email = get_user_email(),
            curr_dog_index = 1,
        )

    return dict(
        # This is the signed URL for the callback.
        update_idx_url = URL('update_idx', signer=url_signer),
        get_user_idx_url = URL('get_user_idx', signer=url_signer),
        set_curr_dogs_url = URL('set_curr_dogs', signer=url_signer),
        get_curr_dogs_url = URL('get_curr_dogs', signer=url_signer),
        add_match_url = URL('add_match',signer=url_signer),
        get_curr_matches_url = URL('get_curr_matches',signer=url_signer),
        get_pref_url = URL('get_pref', signer=url_signer),
        url_signer = url_signer,
        auth = get_user(),
    )

@action('update_idx', method="POST")
@action.uses(url_signer.verify(), db, session, auth.user)
def update_idx():
    idx = request.json.get('disp_cards_idx')
    assert idx is not None
    # if(idx is None):
    #     print("idx is none: ", idx)
    db( db.dbuser.auth == get_user() ).update(
        curr_dog_index = idx
    )
    return "ok"

@action('get_user_idx', method="GET")
@action.uses(url_signer.verify(), db, session, auth.user)
def get_user_idx():
    
    user = db((db.dbuser.auth == get_user() )).select().first()
    assert user is not None
    return dict(user_index=user.curr_dog_index)
 
@action('set_curr_dogs', method='POST')
@action.uses(url_signer.verify(), db, session, auth.user)
def set_curr_dogs():

    # Should take in 20 current pup card information 
    # should also take in the current index 
    # insert 20 dogs into the dog db
    # in turn, adding those 20 dogs into the curr_dogs data base

    user = db(db.dbuser.auth == get_user()).select().first()

    new_pup_cards = request.json.get('new_pup_cards')
    assert new_pup_cards is not None
    # print(new_pup_cards)

    # delete the current curr_dogs list owned by the user
    # get user's curr_dogs list, and dog in that list with pup_idx id
    db(db.curr_dogs.user_owned == user).delete()

    pup_index = 1
    for pup in new_pup_cards:
        curr_entry = db.curr_dogs.insert(
            user_owned=user,
            dog_index=pup_index,
        )
        # print (pup)
        db.dog.insert(
            list_in=curr_entry,
            dog_id=pup["id"],
            dog_name=pup["name"],
            dog_photos=pup["image"],
            dog_breed=pup["breed"],
            dog_age=pup["age"],
            dog_gender=pup["gender"],
            dog_size=pup["size"],
            dog_fur=pup["fur"],
            dog_potty=pup["potty"],
            dog_kid=pup["kid"],
            dog_location=pup["location"],
            dog_url=pup["url"],
        )
        pup_index = pup_index+1

    # session.sleep(5)

    # db(db.curr_dogs.user_owned == user).delete()    
    # db(db.dog).delete()

@action('get_curr_dogs')
@action.uses(url_signer.verify(), db, session, auth.user)
def get_curr_dogs():
    
    pup_idx = request.params.get('pup_idx')
    # print(pup_idx)
    # pup_idx = int(pup_idx)
    assert pup_idx is not None

    # get user's curr_dogs list, and dog in that list with pup_idx id
    user = db(db.dbuser.auth == get_user()).select().first()
    currdogs_dog = db((db.curr_dogs.user_owned == user) & (db.curr_dogs.dog_index == pup_idx)).select().first()
    fished_pup = db( (db.dog.list_in == currdogs_dog) ).select().first()
    # assert fished_pup is not None
    if fished_pup is None:
        return dict(
            empty = True,
        )

    return dict(
        dog_id      =fished_pup.dog_id,
        dog_name    =fished_pup.dog_name,
        dog_breed   =fished_pup.dog_breed,
        dog_age     =fished_pup.dog_age,
        dog_gender  =fished_pup.dog_gender,
        dog_size    =fished_pup.dog_size,
        dog_fur     =fished_pup.dog_fur,
        dog_potty   =fished_pup.dog_potty,
        dog_kid     =fished_pup.dog_kid,
        dog_location=fished_pup.dog_location,
        dog_url     =fished_pup.dog_url,
        dog_photos  =fished_pup.dog_photos
    )


# =============== PROFILE_PAGE.JS =========================
@action('profile/<userID:int>', method="GET")
@action.uses(db, session, auth.user, 'profile.html')
def profile(userID=None):
    assert userID is not None
    user = db.dbuser[userID]
    if user is None:
        redirect(URL('index'))

    # open json files and get list of preference options
    breed_f = open(BREED_JSON_FILE)
    breeds_json = json.load(breed_f)

    # loop though json file load name component into array 
    breed_list = []
    list = breeds_json["breeds"]
    for breed in list:
        breed_list.append(breed["name"])
    # print(breed_list)
    
    colors_list = ["Apricot / Beige",
            "Bicolor",
            "Black",
            "Brindle",
            "Brown / Chocolate",
            "Golden",
            "Gray / Blue / Silver",
            "Harlequin",
            "Merle (Blue)",
            "Merle (Red)",
            "Red / Chestnut / Orange",
            "Sable",
            "Tricolor (Brown, Black, & White)",
            "White / Cream",
            "Yellow / Tan / Blond / Fawn"]

    return dict(
        breed_list = breed_list,
        colors_list = colors_list,
        set_pref_url = URL('set_pref', signer=url_signer),
        get_pref_url = URL('get_pref', signer=url_signer),
        url_signer = url_signer,
        user = user,
        auth = get_user(),
    )

@action('set_pref', method="POST")
@action.uses(url_signer.verify(), db)
def set_pref():
    #  get user
    # print("in set pref")
    
    user = db(db.dbuser.auth == get_user()).select().first()
    assert user is not None

    fish_user_pref = db(db.user_pref.user_owned == user).select().first()
    if fish_user_pref is None:
        db.user_pref.insert(
            user_owned = user,
            breed = request.json.get('breed'),
            size = request.json.get('size'),
            fur = request.json.get('fur'),
            age = request.json.get('age'),
            gender = request.json.get('gender'),
            potty = request.json.get('potty'),
            kid = request.json.get('kid'),
            location = request.json.get('location'),
        )
    else:
        db(db.user_pref.user_owned == user).update(
            breed = request.json.get('breed'),
            size = request.json.get('size'),
            fur = request.json.get('fur'),
            age = request.json.get('age'),
            gender = request.json.get('gender'),
            potty = request.json.get('potty'),
            kid = request.json.get('kid'),
            location = request.json.get('location'),
        )

    return("ok")

@action('get_pref', method="GET")
@action.uses(url_signer.verify(), db)
def get_pref():
    user = db(db.dbuser.auth == get_user()).select().first()
    user_preferences = db((db.user_pref.user_owned == user)).select().first()
    if user_preferences is None:
        db.user_pref.insert(
            user_owned = user,
            breed = "",
            size = "",
            fur = "",
            age = "",
            gender = "",
            potty = "",
            kid = "",
            location = "",
        )

    user_preferences = db((db.user_pref.user_owned == user)).select().first()
    return dict(
            breed = user_preferences.breed,
            age = user_preferences.age,
            size = user_preferences.size,
            fur = user_preferences.fur,
            gender = user_preferences.gender,
            potty = user_preferences.potty,
            kid = user_preferences.kid,
            location = user_preferences.location,
        )


# =============== MATCHES.JS =========================
@action('matches/<userID:int>', method=["GET", "POST"])
@action.uses(db, session, auth.user, 'matches.html')
def matches(userID=None):
    assert userID is not None
    user = db.dbuser[userID]
    
    if user is None:
        redirect(URL('index'))

    return dict(
        get_matches_id_url=URL('get_matches_id',signer=url_signer),
        get_curr_matches_url=URL('get_curr_matches', signer=url_signer),
        delete_match_url=URL('delete_match', signer=url_signer),
        url_signer=url_signer,
        user=user,
        auth = get_user(),
    )

@action('add_match', method="POST")
@action.uses(url_signer.verify(), db, session, auth.user)
def add_match():
    match = request.json.get('match')
    assert match is not None
    match_id = match["id"]
    match_photo = match["image"]
    match_name = match["name"]
    user = db(db.dbuser.auth == get_user()).select().first()
    assert user is not None
    db.recent_matches.insert(
            user_owned=user,
            dog_index=match_id,
            dog_name=match_name,
            dog_images=match_photo,
    )
    matches = db(db.recent_matches.user_owned == user).select()
    len = 0
    for rows in matches:
        len+=1
    if len > 12:
        first_id = matches.first().id
        db(db.recent_matches.id == first_id).delete()
    return "ok"

@action('delete_match')
@action.uses(url_signer.verify(), db)
def delete_comment():
    id = request.params.get('id')
    assert id is not None
    db(db.recent_matches.id == id).delete()
    return "ok"

@action('get_curr_matches', method="GET")
@action.uses(url_signer.verify(), db, session, auth.user)
def get_curr_matches():
    match_id = request.params.get('match_id')
    assert match_id is not None

    # get user's curr_dogs list, and dog in that list with pup_id id
    user = db(db.dbuser.auth == get_user()).select().first()
    fished_pup = db((db.recent_matches.dog_index == match_id)).select().first()
    assert fished_pup is not None
    return dict(
        user_owned=fished_pup.user_owned,
        dog_index=fished_pup.dog_index,
        dog_name=fished_pup.dog_name,
        dog_images=fished_pup.dog_images,
        id=fished_pup.id,
    )

@action('get_matches_id', method="GET")
@action.uses(url_signer.verify(), db, session, auth.user)
def get_matches_id():
    user = db(db.dbuser.auth == get_user()).select().first()
    matches= db(db.recent_matches.user_owned == user).select()
    list = []
    for match in matches:
        list.append(match.dog_index)
    return dict(match_ids= list)

