<template>
	<purple-button class="button-wrapper" @click="onClick">
		<p style="margin: 0">Выгрузить в Excel</p>
		<img v-if="!loading" src="/img/export.svg" />
		<CircleLoader class="circle" v-if="loading"></CircleLoader>
	</purple-button>
</template>
<script setup lang="ts">
import { ref } from "vue";
import CircleLoader from "../UI/CircleLoader.vue";

const props = defineProps({
	callback: {
		type: Function,
		required: true,
	},
});

const loading = ref(false);

const onClick = async () => {
	loading.value = true;
	await props.callback();
	loading.value = false;
};
</script>
<style scoped>
.button-wrapper {
	width: 250px;
	height: 48px;
	background-color: #f5ecf6;
	color: #993ca6;
	font-size: 17px;
	font-family: Stolzl;
	font-weight: 550;

	display: flex;
	flex-direction: row;
	justify-content: center;
	align-items: center;
	gap: 8px;
}
p {
	margin: 0;
}
img {
	margin: 0;
}
.circle {
	width: 20px;
	height: 20px;
	position: unset;
}
</style>
