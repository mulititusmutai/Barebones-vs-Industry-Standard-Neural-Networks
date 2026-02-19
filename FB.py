#EamS
import pygame as pg, time as tm, keyboard as kb, random as rd, math as mt

pg.init()
WIDTH, HEIGHT= 210, 150; GAME= pg.display.set_mode(size=(WIDTH,HEIGHT))
GRAVITY= 32
X, Y= 0, 1
S_W, S_H= 40, 40, ; B_SIZE= 10
WHITE= (230,230,230); CYAN= (0,170,255); BLUE= (20,20,190); BLACK= (10,10,10); RED= (240,150,0)
running= True

def ri():
    return rd.randint(-99,99)/100

def sigmoid(value):
    return 1/(1+ mt.exp(-value))

class Neuron:
    def __init__(self, WnB):
        self.weights= WnB['W']
        self.bias= WnB['B']

    def decide(self, data):
        value= 0
        for c in range(len(data)):
            value+= data[c]*self.weights[c]
        value+= self.bias
        return sigmoid(value)

class NeuralNetwork:
    def __init__(self, WnB):
        self.WnB= WnB        

    def create_neurons(self):
        self.layer1= []
        for n in range(len(self.WnB)-1):
            self.layer1.append(Neuron(self.WnB[n]))
        self.layer2= Neuron(self.WnB[-1])

    def decide(self,state):
        data= []
        for neuron in self.layer1:
            data.append(neuron.decide(state))
        return self.layer2.decide(data)
    
class Bird:
    def __init__(self, space, WnB):        
        self.position= [30,40]
        self.velocity= 0
        self.colors= [BLUE,CYAN]; self.cind= 0        
        self.now= tm.monotonic(); self.start= tm.monotonic()
        self.space= space        
        self.neuralNetwork= NeuralNetwork(WnB); self.neuralNetwork.create_neurons()
        self.died= False
        print(WnB[0]['W'][0])

    def dead(self):
        global running
        dx= self.position[X]-self.space.position[X]; dy= self.position[Y]-self.space.position[Y]
        if self.position[Y]>(HEIGHT- B_SIZE) or self.position[Y]<0 or ((dx>(0-B_SIZE) and dx<S_W) and (dy<0 or dy>(S_H-B_SIZE))):
            self.time= round(tm.monotonic()- self.start,3)
            self.died= True

    def flap(self):
        self.cind= 1; self.now= tm.monotonic()

    def update(self):
        time= tm.monotonic()- self.now       
        self.velocity= -8+ GRAVITY*time
        self.color= self.colors[self.cind]
        self.position= [self.position[X], self.position[Y]+ self.velocity]
        pg.draw.rect(GAME, self.color, (self.position[X], self.position[Y], B_SIZE, B_SIZE))        
        self.dead()
        if time > 0.1:
            self.cind= 0

    def nlze(self, value, min_value, max_value):
        return (value - min_value) / (max_value - min_value)

    def get_state(self):
        dx= self.space.position[X]-self.position[X]-B_SIZE; S_position= S_H/2+ self.space.position[Y]
        return [self.nlze(self.position[Y],0,140), self.nlze(self.velocity,-16,23), self.nlze(dx,-60,200), self.nlze(S_position,40,100)]

    def decide(self):
        state= self.get_state()
        choice= self.neuralNetwork.decide(state)        
        return choice>0.5

class Space:
    def __init__(self):
        self.position= [300, 70]
        self.velocity= -9

    def respawn(self):
        self.position[X]= WIDTH+ (S_W/2)
        self.position[Y]= rd.randint(int(S_H/4), int(HEIGHT-1.25*S_H))        

    def update(self):
        self.position[X]+= self.velocity
        pg.draw.rect(GAME, BLACK, (self.position[X], self.position[Y], S_W, S_H))
        pg.draw.rect(GAME, CYAN, (self.position[X], 0, S_W, self.position[Y]-0))# top pole
        pg.draw.rect(GAME, CYAN, (self.position[X], self.position[Y]+ S_H, S_W, HEIGHT- self.position[Y]))# bottom pole
        ((self.position[X]+ (S_W/2))< 0) and self.respawn()

def crossover(pool,NUM,space):
    birds= []
    for a in range(NUM):
        WnB= []
        for n in range(4):
            s0= rd.choice(pool[0][0]); s1= rd.choice(pool[0][1]); s2= rd.choice(pool[0][2]); s3= rd.choice(pool[0][3]); sb= rd.choice(pool[0][4])
            WnB.append({'W':[s0,s1,s2,s3],'B':sb})
        d0= rd.choice(pool[1][0]); d1= rd.choice(pool[1][1]); d2= rd.choice(pool[1][2]); d3= rd.choice(pool[1][3]); db= rd.choice(pool[1][4])
        WnB.append({'W':[d0,d1,d2,d3],'B':db})
        birds.append(Bird(space,WnB))
    return birds

def mutate(pool,PRC):    
    for HL in pool:
        for d in HL:
            for w in range(len(d)):
                determiner= rd.randint(1,99)/100
                if determiner<=0.1:
                    d[w]+= round(rd.randint(-2,2),2)
    return pool

def get_pool(birds):
    s0=[]; s1=[]; s2=[]; s3=[]; sb=[]; d0=[]; d1=[]; d2=[]; d3=[]; db=[]; 
    for bird in birds:
        for nrn in bird.neuralNetwork.layer1:
            s0.append(nrn.weights[0]); s1.append(nrn.weights[1]); s2.append(nrn.weights[2]); s3.append(nrn.weights[3]); sb.append(nrn.bias)
        nrn2= bird.neuralNetwork.layer2
        d0.append(nrn2.weights[0]); d1.append(nrn2.weights[1]); d2.append(nrn2.weights[2]); d3.append(nrn2.weights[3]); db.append(nrn2.bias)
    return ([s0,s1,s2,s3,sb],[d0,d1,d2,d3,db])

def get_fittest(birds):
    times= [bird.time for bird in birds]
    fit_times= sorted(times, reverse=True)[:5]
    return [birds[times.index(t)] for t in fit_times]

def WnB():
    return ({'W': [ri(), ri(), ri(), ri()], 'B': ri()}, {'W': [ri(), ri(), ri(), ri()], 'B': ri()},
            {'W': [ri(), ri(), ri(), ri()], 'B': ri()}, {'W': [ri(), ri(), ri(), ri()], 'B': ri()},
            {'W': [ri(), ri(), ri(), ri()], 'B': ri()})

space= Space()
NUM= 20; GENS= 500; PRC= 0.1
birds= [Bird(space,WnB()) for _ in range(NUM)]

for g in range(GENS):  
    space.respawn()
    bird_no= NUM
    while bird_no> 0:
        bird_no= 0
        GAME.fill(BLACK)    
        space.update()
        for bird in birds:
            if not bird.died:
                bird_no+= 1
                bird.update()                
                if bird.decide():                    
                    bird.flap()
        GAME.blit(pg.font.Font(None, 48).render(str(g+1), True, RED), (100, 100))
        pg.display.update()
        if kb.is_pressed('esc'):
            running= False; tm.sleep(3)
        tm.sleep(0.05)
    for bird in birds:
        print('time:',bird.time)
        if bird.time>5:
            print(bird.neuralNetwork.WnB)
    fit_birds= get_fittest(birds)
    pool= get_pool(fit_birds)
    mutation= mutate(pool,PRC)
    birds= crossover(mutation,NUM,space)   
