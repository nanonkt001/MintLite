export type Attribute = { trait_type: string; value: string | number };
export type Metadata = {
  name: string; description: string; image?: string; attributes?: Attribute[];
};
export function buildMetadata(input: Metadata){
  return JSON.stringify(input, null, 2);
}
