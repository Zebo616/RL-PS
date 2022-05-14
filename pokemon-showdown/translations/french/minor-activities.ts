import type {Translations} from "../../server/chat";

export const translations: Translations = {
	strings: {
		"The announcement has ended.": "L'annonce est terminée.",
		"Battles do not support announcements.": "Les combats ne permettent pas de faire des annonces.",
		"You are not allowed to use filtered words in announcements.": "Tu n'es pas autorisé à utiliser des mots filtrés dans les annonces.",
		"There is already a poll or announcement in progress in this room.": "Il y a déjà un sondage ou une annonce dans cette room.",
		"An announcement was started by ${user.name}.": "Une annonce a été lancée par ${user.name}.",
		"There is no announcement running in this room.": "Il n'y a actuellement pas d'annonce dans cette room.",
		"There is no timer to clear.": "Il n'y a pas de minuteur à supprimer.",
		"The announcement timer was turned off.": "Le minuteur de l'annonce a été désactivé.",
		"Invalid time given.": "Temps donné invalide.",
		"The announcement timer is off.": "Le minuteur de l'annonce n'est pas actif.",
		"The announcement was ended by ${user.name}.": "L'annonce a été terminée par ${user.name}.",
		"Accepts the following commands:": "Accepte les commandes suivantes :",

		"That option is not selected.": "Cette option n'est pas sélectionnée.",
		"You have already voted for this poll.": "Tu as déjà voté pour ce sondage.",
		"No options selected.": "Pas d'option sélectionnée.",
		"you will not be able to vote after viewing results": "Tu ne seras plus capable de voter après avoir vu les résultats",
		"View results": "Voir les résultats",
		"You can't vote after viewing results": "Tu ne peux pas voter après avoir vu les résultats",
		"The poll has ended &ndash; scroll down to see the results": "Le sondage est terminé &ndash; descends dans le chat pour voir les résultats.",
		"Vote for ${num}": "Voter pour ${num}",
		"Submit your vote": "Soumettre ton vote",
		"Quiz": "Quiz",
		"Poll": "Sondage",
		"Submit": "Soumettre",
		"ended": "terminé",
		"votes": "votes",
		"delete": "supprimé",
		"Poll too long.": "Sondage trop long.",
		"Battles do not support polls.": "Les combats ne permettent pas de faire des sondages.",
		"You are not allowed to use filtered words in polls.": "Tu n'es pas autorisé à utiliser des mots filtrés dans les annonces.",
		"Not enough arguments for /poll new.": "Pas assez d'arguments pour /poll new.",
		"Too many options for poll (maximum is 8).": "Il y a trop d'options pour un sondage (le maximum est de 8).",
		"There are duplicate options in the poll.": "Il y a plusieurs options identiques dans le sondage.",
		"${user.name} queued a poll.": "${user.name} a mis un sondage en attente.",
		"A poll was started by ${user.name}.": "Un sondage a été lancé par ${user.name}.",
		"The queue is already empty.": "La file d'attente est déjà vide.",
		"Cleared poll queue.": "La file d'attente des sondages a été supprimée.",
		"Room \"${roomid}\" not found.": "La salle \"${roomid}\" n'a pas été trouvée.",
		"Can't delete poll at slot ${slotString} - \"${slotString}\" is not a number.": "Impossible de supprimer le sondage en position ${slotString} - \"${slotString}\" n'est pas un nombre.",
		"There is no poll in queue at slot ${slot}.": "Il n'y a pas de sondage dans la file d'attente en position ${slot}.",
		"(${user.name} deleted the queued poll in slot ${slot}.)": "${user.name} a supprimé le poll en attente en position ${slot}.",
		"There is no poll running in this room.": "Il n'y a pas de sondage actuellement dans cette room.",
		"To vote, specify the number of the option.": "Pour voter, spécifiez le numéro de l'option.",
		"Option not in poll.": "L'option n'est pas dans le sondage.",
		"The poll timer was turned off.": "Le minuteur du sondage a été désactivé.",
		"The queued poll was started.": "Le sondage en attente a été lancé.",
		"The poll timer was turned on: the poll will end in ${timeout} minute(s).": "Le minuteur du sondage a été activé : le sondage va se terminer dans ${timeout} minute(s).",
		"The poll timer was set to ${timeout} minute(s) by ${user.name}.": "Le minuteur du sondage a été fixé à ${timeout} minute(s) par ${user.name}.",
		"The poll timer is on and will end in ${poll.timeoutMins} minute(s).": "Le minuteur du sondage est activé et se terminera dans ${poll.timeoutMins} minute(s).",
		"The poll timer is off.": "Le minuteur du sondage est désactivé.",
		"The poll was ended by ${user.name}.": "Le sondage a été terminé par ${user.name}.",
		"Queued polls:": "Sondages en attente :",
		"Refresh": "Rafraîchir",
		"No polls queued.": "Pas de sondages en attente.",
		"#${number} in queue": "#${number} dans la file d'attente",
	},
};
