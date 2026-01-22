🎬 Bouba Discord Netflix Notifier






Un bot Discord qui t’informe automatiquement des nouveautés Netflix directement dans ton serveur !

✨ Fonctionnalités

Notifications automatiques des nouveaux films et séries Netflix.

Configuration simple et rapide.

Suivi par catégorie Netflix (Action, Comédie, Documentaire…).

100% open-source et personnalisable.

🚀 Démo


Exemple de notification envoyée par le bot sur Discord.

⚙️ Prérequis

.NET 6.0+

Token d’un bot Discord

Connexion internet

🛠️ Installation
git clone https://github.com/bouba89/bouba-discord-netflix-notifier.git
cd bouba-discord-netflix-notifier
dotnet restore
dotnet build

🔧 Configuration

Copie appsettings.example.json en appsettings.json

Remplis-le avec tes informations :

{
  "DiscordToken": "TON_TOKEN_DISCORD",
  "ChannelId": "ID_DU_CHANNEL",
  "NetflixCategories": ["Action", "Comédie", "Documentaire"]
}

🎯 Utilisation

Lance le bot avec :

dotnet run


Ton bot se connectera à ton serveur Discord et commencera à notifier les nouveautés Netflix dans le channel configuré.

🤝 Contribution

Les contributions sont bienvenues !

Ouvre une issue pour signaler un bug ou proposer une idée.

Envoie un pull request pour améliorer le projet.

📄 Licence

MIT License – voir LICENSE
 pour plus de détails.
