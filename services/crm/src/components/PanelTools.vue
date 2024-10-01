<template>
	<div class="tools-wrapper">
		<slot></slot>
	</div>
</template>
<script setup lang="ts"></script>
<style scoped>
.tools-wrapper {
	display: flex;
	align-items: center;
	flex-direction: row;
	gap: 20px;
	padding: 12px 12px 12px 20px;
	background-color: #ffffff;
	border-radius: 2000px;
	white-space: nowrap;
	overflow-y: hidden;
	overflow-x: auto;
	max-width: 80%;
	min-width: 0;
	flex-shrink: 0;
	flex-grow: 1;
}

.tools-wrapper::-webkit-scrollbar {
	width: 5px;
	height: 5px;
	border-radius: 2000px;
}

.tools-wrapper::-webkit-scrollbar-track {
	background-color: #e7e7e7;
	margin: 20px;
}

.tools-wrapper::-webkit-scrollbar-thumb:horizontal {
	height: 10px;
	width: 5px;
	height: 15px !important;
	border-radius: 22px;
	background-color: #993ca6;
}
</style>
