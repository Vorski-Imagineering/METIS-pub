# Places at a Gathering — How-to

This guide is for organisers and administrators. It covers keeping a gathering's places
(the main tent, the garden, the dome), choosing each experience's place, and what visitors
see. The full reference is in [Camps & local gatherings](camps-and-gatherings.md#a-gatherings-places)
and [Experiences](experiences.md#where).

## Keep the gathering's places

You need to be able to edit the gathering: a global editor, or one of its organisers.

1. Open the gathering's page in the CRM. The **Places** section is below **Experiences**.
2. Click **Add place**. Fill in:
   - **Name**: required, at most 120 characters, and unique within the gathering ignoring
     case ("main tent" is refused when "Main tent" exists).
   - **Description**: optional plain text, at most 4,000 characters. Line breaks are kept.
   - **Map link**: optional, a web address starting `http://` or `https://`, for example a
     Google Maps pin.
3. Save. The place appears in the list, A–Z.
4. **Photo**: on the place, use **Add photo**. A place has one photo; uploading another
   replaces it. **Remove photo** takes it off.
5. **Edit** renames a place or changes its text. The place's web address stays the same
   after a rename, so links already shared keep working.
6. **Delete** removes a place and its photo. While any experience has that place as its
   Where, deleting is refused, and the message names the experiences. Change their Where
   first.

## Choose an experience's place

1. Open the experience in the CRM. Below **When** there is a **Where** group.
2. Click it and pick one of the gathering's places, or **No place**. You cannot type a new
   place here: add it on the gathering first.
3. Save.

## What visitors see

Nothing is public until the gathering, camp and experience are published, as for any
experience.

- **Next to the time**: the place's name shows beside the experience's time on its public
  page, on the programme cards and on the camp page's agenda.
- **By place**: the programme has a **By place** tab, beside By day and All experiences. It
  lists the places that have experiences A–Z, with experiences by day and time, and
  **Place to be announced** last.
- **Place pages**: each place has its own page at `/view/<gathering>/places/<place>/`, with
  its photo, description, an **Open map** link and the experiences held there. The place's
  name links to it wherever it shows. While the gathering has no public page of its own,
  the name shows without a link.

## Rename the Where field (administrators)

The field's label is a setting on the experience class, so each event can word it its own
way: Mexico's experiences read **Dónde**, for example. This needs Django admin access.

1. In Django admin, open **Metis classes** and the experience class for your event (for
   example **Experience**).
2. In **Config**, open `info_field_groups`. Find the group whose field has the key `where`.
3. Change the group's `title` and the field's `label` to the new wording. Leave the `key`
   (`where`) and the `type` (`place`) as they are: they are what the code reads.
4. Save. Experience pages in the CRM show the new label at once.

Change only the class your event's experiences use. Other events' classes keep their own
wording. The CRM experiences list's column header stays **Where** for every event.
