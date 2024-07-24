<template>
	<div class="panel-wrapper">
		<img src="/img/logo.svg" />
		<div class="menu">
			<div
				class="nav-button"
				v-for="data in props.navigationButtons"
				v-memo="[data.isActive, data.notifyCount]"
				@click="$emit('click', data.id)"
			>
				<div class="notify" v-if="data.notifyCount">
					<p>{{ data.notifyCount }}</p>
				</div>
				<named-button
					:img-src="data.imageSrc"
					:label="data.label"
					:is-active="data.isActive"
					:key="data.id"
				></named-button>
				<div v-if="data.isActive" class="button-decoration"></div>
			</div>
		</div>
		<div class="logout">
			<logout-button @click="$emit('logout')"></logout-button>
		</div>
	</div>
</template>
<script setup lang="ts">
import { NavigationData } from "@/types";

const props = defineProps({
	navigationButtons: {
		type: Array<NavigationData>,
		required: true,
	},
});
const emit = defineEmits(["click", "logout"]);
</script>
<style scoped>
.panel-wrapper {
	display: flex;
	flex-direction: column;
	width: 125px;
	gap: 50px;
	padding: 40px 10px 40px 10px;
	align-items: center;
	background-color: #ffffff;
	height: fit-content;
	flex-grow: 0;
	overflow: hidden;
}
.panel-wrapper img {
	width: 85px;
}
.menu {
	display: flex;
	flex-direction: column;
	gap: 20px;
	align-items: center;
	width: 100%;
	overflow-y: auto;
	overflow-x: hidden;
}
.menu::-webkit-scrollbar {
	width: 5px;
	height: 5px;
	border-radius: 2000px;
}

.menu::-webkit-scrollbar-track {
	background-color: #e7e7e7;
}

.menu::-webkit-scrollbar-thumb:vertical {
	height: 10px;
	width: 5px;
	height: 15px !important;
	border-radius: 22px;
	background-color: #993ca6;
}
.nav-button {
	position: relative;
	width: 100%;
	display: flex;
	justify-content: center;
	align-items: center;
	cursor: pointer;
}
.button-decoration {
	width: 5px;
	position: absolute;
	height: calc(100% + 4px);
	border-radius: 3.5px 0px 0px 3.5px;
	background-color: black;
	right: -10px;
	top: -4px;
	background-color: #993ca6;
}
.notify {
	position: absolute;
	top: -6px;
	right: 32px;
	background-color: #ff003d;
	z-index: 1;
	width: 20px;
	height: 20px;
	border-radius: 20px;
	color: #ffffff;
	font-family: Stolzl;
	display: flex;
	justify-content: center;
	align-items: center;
}
.notify p {
	margin: 0;
}
</style>
