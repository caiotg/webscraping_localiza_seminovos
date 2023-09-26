CREATE DATABASE carros_localiza_seminovos;

USE carros_localiza_seminovos;

CREATE TABLE `carros_a_venda` (
	`montadora` VARCHAR(32) NOT NULL,
	`modelo` VARCHAR(100) NOT NULL,
    `local_venda` VARCHAR(50) NOT NULL,
    `km` INT NOT NULL,
    `ano` VARCHAR(12) NOT NULL,
    `preco` INT NOT NULL,
    `data_atualizacao` DATA NOT NULL
);

CREATE TABLE `carros_vendidos` (
	`montadora` VARCHAR(32) NOT NULL,
	`modelo` VARCHAR(100) NOT NULL,
    `local_venda` VARCHAR(50) NOT NULL,
    `km` INT NOT NULL,
    `ano` VARCHAR(12) NOT NULL,
    `preco` INT NOT NULL,
    `data_atualizacao` DATA NOT NULL
);