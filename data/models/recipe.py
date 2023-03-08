import datetime


class Recipe:

    def __init__(self,
                 ready_in_minutes: int,
                 servings: int,
                 isVegetarian: bool,
                 isVegan: bool,
                 isDairyFree: bool,
                 isGlutenFree: bool,
                 recipe_id: int,
                 full_title: str,
                 url: str,
                 timestamp: datetime,
                 ):
        self.ready_in_minutes = ready_in_minutes
        self.servings = servings
        self.isVegetarian = isVegetarian
        self.isVegan = isVegan
        self.isDairyFree = isDairyFree
        self.isGlutenFree = isGlutenFree
        self.recipe_id = recipe_id
        self.screen_title = full_title
        self.url = url
        self.timestamp = timestamp
        if len(self.screen_title) > 25:
            self.display_title = "{}...".format(self.screen_title[:25])
        else:
            self.display_title = self.screen_title

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            ready_in_minutes=data["readyInMinutes"],
            servings=data["servings"],
            isVegetarian=data["vegetarian"],
            isVegan=data["vegan"],
            isDairyFree=data["dairyFree"],
            isGlutenFree=data["glutenFree"],
            recipe_id=data["id"],
            full_title=data["title"],
            url=data["spoonacularSourceUrl"],
            timestamp=datetime.date.today().strftime("%Y_%m_%d")
        )
