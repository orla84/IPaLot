# -*- coding: utf-8 -*-
"""
Created on Mon Mar 5 13:54:37 2018
@author: Orlando Ciricosta

class Car_handler(n):
    returns n moving cars, each having a target parking spot and a
    sprite group of remaing moving cars to collide with. Moving and static
    also have dedicated sprite groups
    
class Filled_Lot(car_group):
    Creates a filled parking lot at the center of the screen. N_cars will
    be removed from this by the Get_spot method, to accomodate the
    incoming moving cars, then the remaining cars will be added to car_group
    for rendering/collisions

"""

import pygame
from Cars import Car, Static_car
import random

# size of the image to be passed to the neural network for training
NN_img_size = (70,70)
# initial car positions heigth
FROM_BOTTOM = 45

class Car_handler():
    """
    class Car_handler(n):
        returns n moving cars, each having a target parking spot and a
        sprite group of remaing moving cars to collide with. Moving and static
        also have dedicated sprite groups
    """  
    def __init__(self, n):
        
        self.number_of_cars = n
        self.moving_cars = []
        self.collide_with = []
        self.target_positions = []      
        self.static_cars_group = pygame.sprite.Group()
        self.moving_cars_group = pygame.sprite.Group()
        self.lot = Filled_Lot(self.static_cars_group)
        
        # now sample n indexes in len(lot.static_cars_list) in order to
        # create the target parking spots (Get_spot in the following loop)
        # and add the remaining static cars to the sprite group for
        # collision/rendering
        index = random.sample(range(len(self.lot.static_cars_list)), n)
        for i in range(len(self.lot.static_cars_list)):
            if i not in index:
                self.static_cars_group.add( self.lot.static_cars_list[i] )
                
        # and set the moving cars
        for i in range(self.number_of_cars):
            # cars will be at bottom of screen
            car_position = (
                    (i+1) * pygame.display.Info().current_w // (n+1),
                    - pygame.display.Info().current_h + FROM_BOTTOM
                    )            
            self.moving_cars.append( Car(pos=car_position) )
            self.collide_with.append(pygame.sprite.Group())
            
            car = self.moving_cars[i]
            self.moving_cars_group.add(car)
            
            # create parking spot and save target positions
            self.target_positions.append(
                    self.lot.Get_spot(car, index[i])
                    )
            
        # add each car to the colliding group of the other cars 
        for i in range(n):
            for j in range(n):
                if j != i:
                    self.collide_with[i].add(self.moving_cars[j])
                    
    def reset_car(self, i):
        self.moving_cars[i].reset(pos=(
            (i+1) * pygame.display.Info().current_w // (self.number_of_cars+1),
            - pygame.display.Info().current_h + FROM_BOTTOM)
            )
                
    def get_states(self):
        """returns a list of states for each car to feed to policy/value NN.
        State[i] is a list [player, target, moving/static]
        ready for feeding into a multi-input NN:
        - player and target have shape (4,), the positions of the pseudowheels
        - moving/static has shape(4, CAPACITY-1), rect of other cars
        a convolution with few filters will scan the 4-uples for moving/static
        """
        pass
    
#------------------------------------------------------------------------------

class Filled_Lot():
    ''' Creates a filled parking lot at the center of the screen. N_cars will
        be removed from this by the Get_spot method, to accomodate the
        incoming moving cars.
        The design for the matrix of cars is hardcoded: this could be improved
        but YAGNI
        
        The lot will have a row of vertical cars at the center of screen which
        will remain untouched, an equal row below, which can contain free
        parking spots, and a row of horizontal cars at the top, which can have
        free spots for parallel parking.
    '''
    
    def __init__(self, car_group):
        ''' static_cars_list will only contain cars in the outer rows,
        and it will be used to add/remove spots, whilst car_group contains
        all of the static cars for collision purposes '''
        self.static_cars_list = []

        self.N = 12     # cars in the central raw, divisible by 2
        n = self.N//2
        
        x = pygame.display.Info().current_w //2
        y = pygame.display.Info().current_h //2 -50
        
        # get dummy car for dimensions
        car = Static_car((x,y))           
        h = car.rect.h
        w = car.rect.w
        
        delta = 1.22*w*0.5 # half position increment for vertical cars
        dx = delta
        for i in range(n):
            #append cars to the sides for the center row
            car1 = Static_car( (x + dx ,y) )
            car2 = Static_car( (x - dx ,y) )            
            car_group.add(car1)
            car_group.add(car2)
            # then for the bottom row
            car1 = Static_car( (x + dx ,y + 1.1*h) )
            car2 = Static_car( (x - dx ,y + 1.1*h) )
            ''' DO NOT add cars in the list to the collider group now
                as they may be removed when assigning free spots '''
            self.static_cars_list.append(car1)
            self.static_cars_list.append(car2)
            # then for the upper row, with horizontal cars
            dx += delta
            if i%2 == 0:
                car1 = Static_car((x + dx ,y - 1.1*(h+w)*0.5), vertical=False)
                car2 = Static_car((x - dx ,y - 1.1*(h+w)*0.5), vertical=False)          
                self.static_cars_list.append(car1)
                self.static_cars_list.append(car2)            
            dx += delta
            
            
    def Get_spot(self, car, index):
        """ Create a parking spot for car and return its pseudo-wheel
        target positions """
        
        spot = self.static_cars_list[index]
        return spot.get_pseudowheels(car)
    
    
    
    
    
    
    
    