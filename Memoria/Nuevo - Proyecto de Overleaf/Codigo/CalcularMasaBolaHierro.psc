Algoritmo calcularMasaBolaHierro
Const	
	PI=3.141593
	densidad=0.00786	// Kg/cm3
Var	
	diametro: real		// diámetro de esfera (cm) 
	radio: real		// radio de la esfera (cm)  
	volumen: real		// volumen de la esfera
	masa: real		// masa en kg

	Escribir "Introduzca el diámetro (cm): "
	Leer diametro
	radio <- diametro/2
	volumen <- 4* PI * radio * radio * radio/3
	masa <- 0.00786 * volumen
	Escribir "Masa: ", masa, " Kg"
Finalgoritmo
