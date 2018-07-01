#! /bin/python3
from random import randint
import time
import pygame
pygame.init()
screen = pygame.display.set_mode((1200, 600))
# RULES (might modify at the individual level if the data supports this)
multiple_matings = 0 # Can individuals mate more than once?
num_offspring = 2 # How many offspring are created after every mating?
cross_generational_mating = False # Can individuals mate with members of previous generations
life_span = 1 # in generations
generation_time = 5 # in seconds
CRISPR_efficiency = 5 # in percent
max_generation_life_span = 1 # how many generations can pass before an individual dies
types = ['heterozygous', 'homozygous_wt', 'homozygous_modified']
num_generations = 6
total_population = 0

# Input box class, with help from https://stackoverflow.com/questions/46390231/how-to-create-a-text-input-box-with-pygame#
COLOR_INACTIVE = pygame.Color('lightskyblue3')
COLOR_ACTIVE = pygame.Color('dodgerblue2')
FONT = pygame.font.Font(None, 32)


class InputBox:

    def __init__(self, x, y, w, h, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = COLOR_INACTIVE
        self.text = text
        self.txt_surface = FONT.render(text, True, self.color)
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # If the user clicked on the input_box rect.
            if self.rect.collidepoint(event.pos):
                # Toggle the active variable.
                self.active = not self.active
            else:
                self.active = False
            # Change the current color of the input box.
            self.color = COLOR_ACTIVE if self.active else COLOR_INACTIVE
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    print(self.text)
                    self.text = ''
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                # Re-render the text.
                self.txt_surface = FONT.render(self.text, True, self.color)

    def update(self):
        # Resize the box if the text is too long.
        width = max(200, self.txt_surface.get_width()+10)
        self.rect.w = width

    def draw(self, screen):
        # Blit the text.
        screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
        # Blit the rect.
        pygame.draw.rect(screen, self.color, self.rect, 2)

class Population:
    def __init__(self, size=0, type=1):
        # keep track of population numbers
        self.homozygous_modified = 0
        self.homozygous_wt = 0
        self.heterozygous = 0
        self.size = size # number of individuals in the population
        self.individuals = []
        self.num_generations = 0
        self.dead = 0
        self.type = type
        # generate initial set of individuals
        for i in range(1, size + 1):
            individual = Individual(i)
            individual.population = self
            if self.type is 0:
                individual.make_heterozygous()
            elif self.type is 1:
                individual.make_homozygous_wt()
            elif self.type is 2:
                individual.make_homozygous_modified()
            else:
                individual.make_homozygous_wt()
            rand = randint(1, 2)
            if rand is 1:
                individual.male = True
            else:
                individual.male = False
            self.individuals.append(individual)
    # Ex. combine modified population with natural population
    # list of individuals in the population
    def merge_with(self, population, init=False):
        # extract individuals from other population and combine
        self.add_individuals(population.individuals, init)
    def add_individuals(self, individuals, init=False):
        for individual in individuals:
            individual.population = self
            # Only update genotype counts if merging populations
            # else we handle this with the mate() function
            if init:
                if individual.is_heterozygous():
                    individual.population.heterozygous += 1
                if individual.is_homozygous_modified():
                    individual.population.homozygous_modified += 1
                if individual.is_homozygous_wt():
                    individual.population.homozygous_wt += 1
        self.individuals += individuals
        self.size += len(individuals) - 1 # update size of current population
    def draw_bugs(self):
        for individual in self.individuals:
            screen.blit(individual.bug['image'], (individual.bug['x'], individual.bug['y']))
            pygame.display.flip()
            # time.sleep(5)
    # Begin mating process, run simulation
    def run(self):
        # Time to represent each generation in a visual simulation in seconds
        for i in range(1, num_generations + 1):
            # Loop through all individuals in the population and have them mate()
            # only need to loop through one sex
            for j in range(1, len(self.individuals)):
                if self.individuals[j].male:
                    self.individuals[j].mate(i)
            # time.sleep(generation_time) # wait the decided number of seconds for visual simulation of generations

class Individual:
    def __init__(self, ID=0, generation=1, male=True, chromosome_one=False, chromosome_two=False, population=None, num_matings=0, dead=False):
        self.id = ID
        self.population = population # what population is this individual a part of?
        # Pretend that every individual has 2 chromosomes since they are diploid and we
        # will be modifying only one trait
        # Use True to signify modified trait
        # False = Wild-Type chromosome
        self.chromosome_one = chromosome_one
        self.chromosome_two = chromosome_two
        # if male = false then female else male
        self.male = male
        self.generation = generation
        self.num_matings = num_matings
        self.dead = dead
        self.bug = {}
        # if visualizing
    # create a bug visualization for this individual
    def create_bug(self, _type):
        bug = pygame.image.load('{}.png'.format(_type)).convert_alpha()
        bug = pygame.transform.smoothscale(bug, (50, 50))
        bug = pygame.transform.rotozoom(bug, 90, 1)
        self.bug['image'] = bug
        # Algorithm to determine x and y here
        # We'll just put them in random positions within good margins of the screen
        # Avoiding the interface
        self.bug['x'] = randint(10, 1150)
        self.bug['y'] = randint(110, 550)
        # screen.blit(bug, (x, y))
        # pygame.display.flip()

    def is_heterozygous(self):
        return self.chromosome_one != self.chromosome_two
    def is_homozygous_modified(self):
        return self.chromosome_one == True and self.chromosome_two == True
    def is_homozygous_wt(self):
        return self.chromosome_one == False and self.chromosome_two == False
    def make_heterozygous(self):
        # self.chromosome_one = False
        # self.chromosome_two = True
        # self.population.heterozygous += 1
        # CRISPR makes it homozygous no matter what
        self.make_homozygous_modified()
    def make_homozygous_modified(self):
        self.chromosome_one = True
        self.chromosome_two = True
        self.population.homozygous_modified += 1
        self.create_bug('mod')
    def make_homozygous_wt(self):
        self.chromosome_one = False
        self.chromosome_two = False
        self.population.homozygous_wt += 1
        self.create_bug('wt')
    # mate with another individual in the same population
    def mate(self, current_generation):
        """
        Important variables:
        Can individuals mate more than once?
        How much offspring is produced per mating period?
        Can individuals mate with members of the previous generation?
        # Let's solve these problems by making them all an option in RULES

        1.Choose a random indi
        vidual of the opposite sex,
        with number_of_matings <= multiple_matings and generation = self.generation (if cross_generational_mating == False)
        2.Combine chromosome values based on Punnet Square stuff
        3.Create new individuals with above chromosome probabilities, generation = self.generation + 1
        4.Add new individual to self.population
        """
        # You can't mate if you're dead
        if not self.dead:
            #1
            mateless = True
            mate = None # check if this needs to be instantiated outside of while loop
            tries = 1
            clear = False
            while mateless:
                # get a random ID from the population
                ID = randint(1, self.population.size - 1)
                # make sure it fits constraints:
                mate = self.population.individuals[ID]
                # they are clear if it is legal to mate cross_generation or if they are in the same generation
                if cross_generational_mating == False:
                    if mate.generation == self.generation:
                        clear = True
                else:
                    clear = True

                if mate.num_matings <= multiple_matings and self.num_matings <= multiple_matings and mate.male is False and clear:
                    # constraints are met! We can stop looking and actually mate
                    mateless = False
                tries +=1
                if tries > 10:
                    return # They lost their opportunity to mate
            #2 & 3
            # create proper number of individuals based on inheritance probabilities
            children = []
            for i in range(1, num_offspring + 1):
                rand = randint(1, 2)
                if rand == 1:
                    male = True
                else:
                    male = False
                child = Individual(self.population.size + i, self.generation + 1, male, False, False, self.population)
                if self.is_homozygous_modified() and mate.is_homozygous_modified():
                    child.make_homozygous_modified()
                elif self.is_heterozygous() and mate.is_heterozygous():
                    rand = randint(1, 4)
                    if rand == 1:
                        child.make_homozygous_modified()
                    if rand == 2 or rand == 3:
                        child.make_heterozygous()
                    else:
                        child.make_homozygous_wt()
                elif self.is_homozygous_wt() and mate.is_homozygous_wt():
                    child.make_homozygous_wt()
                elif (self.is_homozygous_wt() and mate.is_homozygous_modified()) or (mate.is_homozygous_wt() and self.is_homozygous_modified()):
                    child.make_heterozygous()
                elif (self.is_heterozygous() and mate.is_homozygous_wt()) or (mate.is_heterozygous() and self.is_homozygous_wt()):
                    rand = randint(1, 2)
                    if rand == 1:
                        child.make_heterozygous()
                    else:
                        child.make_homozygous_wt()
                elif (self.is_heterozygous() and mate.is_homozygous_modified()) or (self.is_homozygous_modified() and mate.is_heterozygous()):
                    rand = randint(1, 2)
                    if rand == 1:
                        child.make_heterozygous()
                    else:
                        child.make_homozygous_wt()
                else:
                    # apparently we missed something
                    print('{}, {}'.format(self.chromosome_one, self.chromosome_two))
                    print('{}, {}'.format(mate.chromosome_one, mate.chromosome_two))
                    print("Apparently you missed something.")
                children.append(child)
            #4
            self.population.add_individuals(children)
            #update the status of this individual to have mated
            self.num_matings += 1
            # check how many generations currently exist
            # if greater than certain amount they are old so parent dies
            if current_generation - self.generation > max_generation_life_span:
                self.dead = True
                self.population.dead +=1

def get_stats(population):
    # Output total size of population,
    # amount homozygous_modified, heterozygous, and homozygous_wt
    print("Total Population size after {} generations: {}".format(num_generations, len(population.individuals)))
    print("Total Homozygous modified: {}, heterozygous: {}, homozygous wt: {}".format(population.homozygous_modified, population.heterozygous, population.homozygous_wt))

def main(wild_type_pop_size=None, modified_pop_size=None):
    # terminal version -- collect inputs
    if wild_type_pop_size is None:
        wild_type_pop_size = int(input("Enter size of the initial population: "))
        modified_pop_size = int(input("Enter size of the modified population you want to introduce: "))
    life_span = 0
    # Develop parameters for modified population
    modified_population = Population(modified_pop_size, 2) # all homozygous_modified
    # Develop parameters for initial wild-type population
    wild_type_population = Population(wild_type_pop_size)
    wild_type_population.merge_with(modified_population, True)
    # Begin simulation
    # Note: wild_type_population now contains both wild_type and modified populations combined
    wild_type_population.run()
    get_stats(wild_type_population)
    population = wild_type_population
    return {
        'generations': num_generations,
        'population': population,
    }

# main()


# Start visualization code
def simulation():
    clock = pygame.time.Clock()
    done = False
    wt_population_input = InputBox(30, 30, 200, 30)
    mod_population_input = InputBox(30, 75, 200, 30)
    while not done:
        screen.fill((255, 255, 255))
        input_boxes = [wt_population_input, mod_population_input]
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            for box in input_boxes:
                box.handle_event(event)
        for box in input_boxes:
            box.update()
        # Create interface
        # Inputs
        for box in input_boxes:
            box.draw(screen)
        # Start button rectangle
        button_x = 250
        button_y = 35
        button_width = 120
        button_height = 60
        pygame.draw.rect(screen, (0, 128, 255), pygame.Rect(button_x, button_y, button_width, button_height))
        font = pygame.font.SysFont("comicsansms", 26)
        # Simulation info
        # instantiate info if it doesn't already exist
        try:
            generation_num
        except NameError:
            generation_num = 0
            wt_num = 0
            mod_num = 0
            population = None

        if population is not None:
            population.draw_bugs()
        generation = font.render("Generation: {}".format(generation_num), True, (0, 0, 0))
        num_wt = font.render("% Wild-Type (red): {}".format(wt_num), True, (0, 0, 0))
        num_mod = font.render("% Modified (blue): {}".format(mod_num), True, (0, 0, 0))
        pygame.display.flip()
        # Start button text
        button = font.render("Start", True, (0, 0, 0))
        # Render everything
        screen.blit(generation, (520 - generation.get_width() // 2, 40 - generation.get_height() // 2))
        screen.blit(num_wt, (740 - num_wt.get_width() // 2, 40 - num_wt.get_height() // 2))
        screen.blit(num_mod, (980 - num_mod.get_width() // 2, 40 - num_mod.get_height() // 2))
        screen.blit(button, (230 + (120 / 2), 28 + (60 / 2)))
        # Start Button Listener
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        # if mouse is hovering AND click
        if button_x + button_width > mouse[0] > button_x and button_y + button_height > mouse[1] > button_y:
            if click[0] == 1:
                results = main(int(wt_population_input.text), int(mod_population_input.text)) # run simulation on click!
                population = results['population']
                generation_num = results['generations']
                wt_num = population.homozygous_wt
                mod_num = population.homozygous_modified
                pygame.display.flip()
        pygame.display.flip()
        clock.tick(60)
        # main() # run main program
        # pygame.display.flip()

simulation()
